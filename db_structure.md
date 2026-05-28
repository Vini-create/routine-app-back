Pensou por 17s

Boa correção. Eu também revisaria para uma estrutura mais enxuta, robusta e menos redundante.

A ideia principal: não duplicar dado que já está dentro de JSON, não criar tabela para tudo antes da necessidade real e manter o banco fácil de evoluir. Pela LGPD, isso também conversa melhor com o princípio de necessidade: guardar apenas dados úteis para a finalidade do app, evitando coleta excessiva de dados pessoais.

Abaixo está uma versão mais limpa, já no estilo que você usaria com SQLAlchemy 2.0.

Estrutura final revisada
users
├── user_credentials
├── refresh_tokens
├── user_preferences
├── coach_profiles
├── goals
├── habits
│   └── habit_logs
├── routine_items
│   └── routine_item_logs
├── chat_sessions
│   └── chat_messages
├── feedbacks
├── knowledge_documents
│   └── knowledge_chunks
├── ai_usage_logs
└── user_consents

Eu removi/evitaria por enquanto:

goal_checkins
rag_retrieval_logs
feedback strengths/weaknesses/recommendations separados
routine_snapshot/habits_snapshot/goals_snapshot em colunas separadas
muitos campos de auditoria desnecessários

No caso dos feedbacks, você está certo: melhor guardar um JSON gerado pelo Feedbacker e pronto.

Base dos models
import uuid
from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Time,
    Integer,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
1. users

Tabela principal do usuário.

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(80),
        default="America/Sao_Paulo",
        nullable=False,
    )

    locale: Mapped[str] = mapped_column(
        String(10),
        default="pt-BR",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    credentials: Mapped["UserCredential"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

Eu não colocaria CPF, RG, endereço, telefone ou data de nascimento. Para esse app, isso não é necessário.

2. user_credentials

Separação dos dados de login.

class UserCredential(Base, TimestampMixin):
    __tablename__ = "user_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    password_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="credentials")

Aqui você guarda só o hash da senha. Nada de senha pura.

3. refresh_tokens

Para JWT com refresh token.

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    device_label: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

Eu tirei ip_hash e user_agent_hash daqui para simplificar. Você pode adicionar depois se quiser auditoria de segurança mais forte.

4. user_preferences

Preferências básicas do app.

class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        default="system",
        nullable=False,
    )

    notification_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    reminder_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    week_starts_on: Mapped[str] = mapped_column(
        String(10),
        default="monday",
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="preferences")

Removi ai_response_style porque isso fica melhor em coach_profiles.

5. coach_profiles

Perfil do CoachBot.

class CoachProfile(Base, TimestampMixin):
    __tablename__ = "coach_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    style: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

Eu tirei system_prompt daqui no MVP. Melhor o backend controlar os prompts. Se o prompt ficar editável pelo usuário, aumenta risco de prompt injection e bagunça no comportamento.

6. goals

Metas do usuário.

class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    target_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    progress_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Removi start_date porque o created_at já cumpre esse papel na maioria dos casos.

7. habits

Hábitos do usuário.

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    frequency_type: Mapped[str] = mapped_column(
        String(30),
        default="daily",
        nullable=False,
    )

    target_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    target_unit: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True,
    )

    consistency_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    best_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Removi difficulty. É legal, mas não essencial agora. Se quiser voltar depois, fácil.

8. habit_logs

Registros de execução dos hábitos.

class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    completed_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_log_per_day"),
        Index("ix_habit_logs_user_date", "user_id", "log_date"),
    )

Aqui user_id é redundante tecnicamente, porque dá para chegar pelo hábito. Mas vale manter para query rápida e isolamento por usuário.

9. routine_items

Itens da rotina.

class RoutineItem(Base, TimestampMixin):
    __tablename__ = "routine_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    item_type: Mapped[str] = mapped_column(
        String(40),
        default="task",
        nullable=False,
    )

    scheduled_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Essa tabela está boa. Ela é flexível sem exagerar.

10. routine_item_logs

Registros dos itens da rotina.

class RoutineItemLog(Base, TimestampMixin):
    __tablename__ = "routine_item_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    routine_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routine_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "routine_item_id",
            "log_date",
            name="uq_routine_item_log_per_day",
        ),
        Index("ix_routine_logs_user_date", "user_id", "log_date"),
    )

Removi started_at, completed_at e delay_minutes. Para MVP, isso complica mais do que ajuda. Depois, se você quiser analytics mais fino de pontualidade, adiciona.

11. chat_sessions

Sessões do CoachBot.

class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    coach_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Essa tabela vale manter, porque facilita separar conversas.

12. chat_messages

Mensagens do CoachBot.

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(30),
        default="text",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )

Removi token_count e model_name daqui. Isso fica melhor em ai_usage_logs.

13. feedbacks

Feedbacks gerados pelo Feedbacker.

Aqui fica bem mais limpo.

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_feedbacks_user_created", "user_id", "created_at"),
    )

Exemplo do JSON salvo em content:

{
  "title": "Análise da sua rotina semanal",
  "summary": "Você teve boa consistência nos hábitos principais, mas sua rotina da manhã está sobrecarregada.",
  "strengths": [
    "Boa execução nos hábitos ligados à meta principal",
    "Consistência alta nos dias úteis"
  ],
  "weaknesses": [
    "Queda de execução no fim de semana",
    "Muitos itens acumulados no período da manhã"
  ],
  "recommendations": [
    {
      "title": "Reduzir carga da manhã",
      "description": "Mover tarefas menos importantes para a tarde.",
      "priority": "high"
    }
  ],
  "analyzed_period": {
    "start_date": "2026-05-20",
    "end_date": "2026-05-26"
  }
}

Esse modelo é muito melhor para seu caso. Simples, flexível e sem duplicar estrutura.

14. knowledge_documents

Documentos da base de conhecimento do Feedbacker.

class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_hash: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

Removi source_name, porque title + source_type + metadata nos chunks já resolvem.

15. knowledge_chunks

Chunks para RAG.

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    meta: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
    )

Para o embedding, eu não colocaria agora se você ainda não for implementar pgvector. Quando for implementar, adiciona:

from pgvector.sqlalchemy import Vector

embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)

Mas só coloca quando for usar mesmo.

16. ai_usage_logs

Logs de uso da IA.

class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    feature_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    input_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_ai_usage_user_created", "user_id", "created_at"),
        Index("ix_ai_usage_feature_created", "feature_name", "created_at"),
    )

Removi estimated_cost e error_message. Para MVP, status já resolve. Se quiser debug real depois, adiciona error_code, não mensagem gigante.

17. user_consents

Consentimentos.

class UserConsent(Base):
    __tablename__ = "user_consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    consent_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

Removi accepted_at e revoked_at. Para MVP, cada registro representa um evento de consentimento. Se o usuário revogar, você cria outro registro com accepted=False.

Relações principais
users 1---1 user_credentials
users 1---N refresh_tokens
users 1---1 user_preferences
users 1---N coach_profiles

users 1---N goals
users 1---N habits
goals 1---N habits

habits 1---N habit_logs

users 1---N routine_items
goals 1---N routine_items
routine_items 1---N routine_item_logs

users 1---N chat_sessions
coach_profiles 1---N chat_sessions
chat_sessions 1---N chat_messages

users 1---N feedbacks
goals 1---N feedbacks

knowledge_documents 1---N knowledge_chunks

users 1---N ai_usage_logs
users 1---N user_consents
Índices importantes
users.email

refresh_tokens.user_id
refresh_tokens.token_hash

goals.user_id
goals.status

habits.user_id
habits.goal_id
habits.status

habit_logs.user_id + log_date
habit_logs.habit_id + log_date

routine_items.user_id
routine_items.goal_id
routine_items.status

routine_item_logs.user_id + log_date
routine_item_logs.routine_item_id + log_date

chat_sessions.user_id
chat_messages.session_id + created_at

feedbacks.user_id + created_at

knowledge_chunks.document_id

ai_usage_logs.user_id + created_at
ai_usage_logs.feature_name + created_at

user_consents.user_id
O que eu implementaria primeiro

Para o MVP real:

users
user_credentials
refresh_tokens
user_preferences
coach_profiles
goals
habits
habit_logs
routine_items
routine_item_logs
chat_sessions
chat_messages
feedbacks
ai_usage_logs
user_consents

Depois, quando for ativar RAG:

knowledge_documents
knowledge_chunks
Estrutura de pastas recomendada
app/
├── db/
│   ├── base.py
│   └── session.py
│
├── models/
│   ├── user.py
│   ├── auth.py
│   ├── preferences.py
│   ├── coach.py
│   ├── goal.py
│   ├── habit.py
│   ├── routine.py
│   ├── chat.py
│   ├── feedback.py
│   ├── knowledge.py
│   ├── ai_usage.py
│   └── consent.py
│
├── schemas/
│   ├── user.py
│   ├── auth.py
│   ├── goal.py
│   ├── habit.py
│   ├── routine.py
│   ├── chat.py
│   └── feedback.py
│
├── services/
│   ├── auth_service.py
│   ├── coachbot_service.py
│   ├── feedbacker_service.py
│   ├── context_builder.py
│   ├── habit_service.py
│   ├── routine_service.py
│   ├── goal_service.py
│   └── ai_usage_service.py
│
└── repositories/
    ├── user_repository.py
    ├── goal_repository.py
    ├── habit_repository.py
    ├── routine_repository.py
    ├── chat_repository.py
    └── feedback_repository.py
Minha opinião final

Essa versão ficou bem melhor.

Agora o banco está com cara de projeto profissional porque ele tem:

- autenticação separada
- refresh tokens com hash
- usuários com soft delete
- metas, hábitos e rotina bem modelados
- logs de execução
- CoachBot com sessões e mensagens
- Feedbacker com JSON flexível
- estrutura futura para RAG
- logs de uso de IA
- consentimentos básicos

E ao mesmo tempo você não está criando tabela para tudo cedo demais.

A regra aqui é boa: se o dado só serve para compor o feedback gerado, guarda dentro do JSON do feedback. Se o dado precisa ser consultado, filtrado, ordenado ou atualizado com frequência, vira coluna/tabela própria.

o que é esse mapped? é um pouco diferente do que eu usavaPensou por 17s

Boa correção. Eu também revisaria para uma estrutura mais enxuta, robusta e menos redundante.

A ideia principal: não duplicar dado que já está dentro de JSON, não criar tabela para tudo antes da necessidade real e manter o banco fácil de evoluir. Pela LGPD, isso também conversa melhor com o princípio de necessidade: guardar apenas dados úteis para a finalidade do app, evitando coleta excessiva de dados pessoais.

Abaixo está uma versão mais limpa, já no estilo que você usaria com SQLAlchemy 2.0.

Estrutura final revisada
users
├── user_credentials
├── refresh_tokens
├── user_preferences
├── coach_profiles
├── goals
├── habits
│   └── habit_logs
├── routine_items
│   └── routine_item_logs
├── chat_sessions
│   └── chat_messages
├── feedbacks
├── knowledge_documents
│   └── knowledge_chunks
├── ai_usage_logs
└── user_consents

Eu removi/evitaria por enquanto:

goal_checkins
rag_retrieval_logs
feedback strengths/weaknesses/recommendations separados
routine_snapshot/habits_snapshot/goals_snapshot em colunas separadas
muitos campos de auditoria desnecessários

No caso dos feedbacks, você está certo: melhor guardar um JSON gerado pelo Feedbacker e pronto.

Base dos models
import uuid
from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Time,
    Integer,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
1. users

Tabela principal do usuário.

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    display_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(80),
        default="America/Sao_Paulo",
        nullable=False,
    )

    locale: Mapped[str] = mapped_column(
        String(10),
        default="pt-BR",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    credentials: Mapped["UserCredential"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

Eu não colocaria CPF, RG, endereço, telefone ou data de nascimento. Para esse app, isso não é necessário.

2. user_credentials

Separação dos dados de login.

class UserCredential(Base, TimestampMixin):
    __tablename__ = "user_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    password_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="credentials")

Aqui você guarda só o hash da senha. Nada de senha pura.

3. refresh_tokens

Para JWT com refresh token.

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    device_label: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

Eu tirei ip_hash e user_agent_hash daqui para simplificar. Você pode adicionar depois se quiser auditoria de segurança mais forte.

4. user_preferences

Preferências básicas do app.

class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        default="system",
        nullable=False,
    )

    notification_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    reminder_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    week_starts_on: Mapped[str] = mapped_column(
        String(10),
        default="monday",
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="preferences")

Removi ai_response_style porque isso fica melhor em coach_profiles.

5. coach_profiles

Perfil do CoachBot.

class CoachProfile(Base, TimestampMixin):
    __tablename__ = "coach_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    style: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

Eu tirei system_prompt daqui no MVP. Melhor o backend controlar os prompts. Se o prompt ficar editável pelo usuário, aumenta risco de prompt injection e bagunça no comportamento.

6. goals

Metas do usuário.

class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    target_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    progress_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Removi start_date porque o created_at já cumpre esse papel na maioria dos casos.

7. habits

Hábitos do usuário.

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    frequency_type: Mapped[str] = mapped_column(
        String(30),
        default="daily",
        nullable=False,
    )

    target_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    target_unit: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True,
    )

    consistency_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    best_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Removi difficulty. É legal, mas não essencial agora. Se quiser voltar depois, fácil.

8. habit_logs

Registros de execução dos hábitos.

class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    completed_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_log_per_day"),
        Index("ix_habit_logs_user_date", "user_id", "log_date"),
    )

Aqui user_id é redundante tecnicamente, porque dá para chegar pelo hábito. Mas vale manter para query rápida e isolamento por usuário.

9. routine_items

Itens da rotina.

class RoutineItem(Base, TimestampMixin):
    __tablename__ = "routine_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    item_type: Mapped[str] = mapped_column(
        String(40),
        default="task",
        nullable=False,
    )

    scheduled_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True,
    )

    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Essa tabela está boa. Ela é flexível sem exagerar.

10. routine_item_logs

Registros dos itens da rotina.

class RoutineItemLog(Base, TimestampMixin):
    __tablename__ = "routine_item_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    routine_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routine_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "routine_item_id",
            "log_date",
            name="uq_routine_item_log_per_day",
        ),
        Index("ix_routine_logs_user_date", "user_id", "log_date"),
    )

Removi started_at, completed_at e delay_minutes. Para MVP, isso complica mais do que ajuda. Depois, se você quiser analytics mais fino de pontualidade, adiciona.

11. chat_sessions

Sessões do CoachBot.

class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    coach_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

Essa tabela vale manter, porque facilita separar conversas.

12. chat_messages

Mensagens do CoachBot.

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(30),
        default="text",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )

Removi token_count e model_name daqui. Isso fica melhor em ai_usage_logs.

13. feedbacks

Feedbacks gerados pelo Feedbacker.

Aqui fica bem mais limpo.

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
    )

    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_feedbacks_user_created", "user_id", "created_at"),
    )

Exemplo do JSON salvo em content:

{
  "title": "Análise da sua rotina semanal",
  "summary": "Você teve boa consistência nos hábitos principais, mas sua rotina da manhã está sobrecarregada.",
  "strengths": [
    "Boa execução nos hábitos ligados à meta principal",
    "Consistência alta nos dias úteis"
  ],
  "weaknesses": [
    "Queda de execução no fim de semana",
    "Muitos itens acumulados no período da manhã"
  ],
  "recommendations": [
    {
      "title": "Reduzir carga da manhã",
      "description": "Mover tarefas menos importantes para a tarde.",
      "priority": "high"
    }
  ],
  "analyzed_period": {
    "start_date": "2026-05-20",
    "end_date": "2026-05-26"
  }
}

Esse modelo é muito melhor para seu caso. Simples, flexível e sem duplicar estrutura.

14. knowledge_documents

Documentos da base de conhecimento do Feedbacker.

class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_hash: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

Removi source_name, porque title + source_type + metadata nos chunks já resolvem.

15. knowledge_chunks

Chunks para RAG.

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    meta: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
    )

Para o embedding, eu não colocaria agora se você ainda não for implementar pgvector. Quando for implementar, adiciona:

from pgvector.sqlalchemy import Vector

embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=True)

Mas só coloca quando for usar mesmo.

16. ai_usage_logs

Logs de uso da IA.

class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    feature_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    input_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_ai_usage_user_created", "user_id", "created_at"),
        Index("ix_ai_usage_feature_created", "feature_name", "created_at"),
    )

Removi estimated_cost e error_message. Para MVP, status já resolve. Se quiser debug real depois, adiciona error_code, não mensagem gigante.

17. user_consents

Consentimentos.

class UserConsent(Base):
    __tablename__ = "user_consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    consent_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    accepted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

Removi accepted_at e revoked_at. Para MVP, cada registro representa um evento de consentimento. Se o usuário revogar, você cria outro registro com accepted=False.

Relações principais
users 1---1 user_credentials
users 1---N refresh_tokens
users 1---1 user_preferences
users 1---N coach_profiles

users 1---N goals
users 1---N habits
goals 1---N habits

habits 1---N habit_logs

users 1---N routine_items
goals 1---N routine_items
routine_items 1---N routine_item_logs

users 1---N chat_sessions
coach_profiles 1---N chat_sessions
chat_sessions 1---N chat_messages

users 1---N feedbacks
goals 1---N feedbacks

knowledge_documents 1---N knowledge_chunks

users 1---N ai_usage_logs
users 1---N user_consents
Índices importantes
users.email

refresh_tokens.user_id
refresh_tokens.token_hash

goals.user_id
goals.status

habits.user_id
habits.goal_id
habits.status

habit_logs.user_id + log_date
habit_logs.habit_id + log_date

routine_items.user_id
routine_items.goal_id
routine_items.status

routine_item_logs.user_id + log_date
routine_item_logs.routine_item_id + log_date

chat_sessions.user_id
chat_messages.session_id + created_at

feedbacks.user_id + created_at

knowledge_chunks.document_id

ai_usage_logs.user_id + created_at
ai_usage_logs.feature_name + created_at

user_consents.user_id
O que eu implementaria primeiro

Para o MVP real:

users
user_credentials
refresh_tokens
user_preferences
coach_profiles
goals
habits
habit_logs
routine_items
routine_item_logs
chat_sessions
chat_messages
feedbacks
ai_usage_logs
user_consents

Depois, quando for ativar RAG:

knowledge_documents
knowledge_chunks
Estrutura de pastas recomendada
app/
├── db/
│   ├── base.py
│   └── session.py
│
├── models/
│   ├── user.py
│   ├── auth.py
│   ├── preferences.py
│   ├── coach.py
│   ├── goal.py
│   ├── habit.py
│   ├── routine.py
│   ├── chat.py
│   ├── feedback.py
│   ├── knowledge.py
│   ├── ai_usage.py
│   └── consent.py
│
├── schemas/
│   ├── user.py
│   ├── auth.py
│   ├── goal.py
│   ├── habit.py
│   ├── routine.py
│   ├── chat.py
│   └── feedback.py
│
├── services/
│   ├── auth_service.py
│   ├── coachbot_service.py
│   ├── feedbacker_service.py
│   ├── context_builder.py
│   ├── habit_service.py
│   ├── routine_service.py
│   ├── goal_service.py
│   └── ai_usage_service.py
│
└── repositories/
    ├── user_repository.py
    ├── goal_repository.py
    ├── habit_repository.py
    ├── routine_repository.py
    ├── chat_repository.py
    └── feedback_repository.py
Minha opinião final

Essa versão ficou bem melhor.

Agora o banco está com cara de projeto profissional porque ele tem:

- autenticação separada
- refresh tokens com hash
- usuários com soft delete
- metas, hábitos e rotina bem modelados
- logs de execução
- CoachBot com sessões e mensagens
- Feedbacker com JSON flexível
- estrutura futura para RAG
- logs de uso de IA
- consentimentos básicos

E ao mesmo tempo você não está criando tabela para tudo cedo demais.

A regra aqui é boa: se o dado só serve para compor o feedback gerado, guarda dentro do JSON do feedback. Se o dado precisa ser consultado, filtrado, ordenado ou atualizado com frequência, vira coluna/tabela própria.

o que é esse mapped? é um pouco diferente do que eu usava