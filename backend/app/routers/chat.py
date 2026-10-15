import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.deps import get_db, get_current_user
from app import models, schemas
from app.services.llm import run_llm

router = APIRouter(tags=["chat"])


def _to_llm_messages(db: Session, conversation_id: str) -> list[dict]:
    rows = db.execute(
        select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at)
    ).scalars().all()

    out = []
    for m in rows:
        entry = {"role": m.role, "content": m.content or ""}
        if m.tool_calls:
            entry["tool_calls"] = m.tool_calls
        if m.role == "tool" and m.tool_call_id:
            entry["tool_call_id"] = m.tool_call_id
        out.append(entry)
    return out


@router.post("/chat", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Get or create conversation
    if payload.conversation_id:
        conv = db.get(models.Conversation, payload.conversation_id)
        if not conv or conv.user_id != user.id:
            raise HTTPException(404, "Conversation not found")
    else:
        conv = models.Conversation(user_id=user.id, title=payload.message[:60])
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Persist user message
    user_msg = models.Message(conversation_id=conv.id, role="user", content=payload.message)
    db.add(user_msg)
    db.commit()

    # 3. Load history + call LLM
    llm_messages = _to_llm_messages(db, conv.id)
    result = run_llm(llm_messages)

    # 4. Persist assistant message
    assistant_msg = models.Message(
        conversation_id=conv.id,
        role="assistant",
        content=result["content"],
        tool_calls=result["raw_tool_calls"],
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # 5. If tool call, create PendingApproval — DO NOT execute
    approval_out = None
    if result["tool_calls"]:
        tc = result["tool_calls"][0]
        approval = models.PendingApproval(
            user_id=user.id,
            conversation_id=conv.id,
            message_id=assistant_msg.id,
            tool_call_id=tc["id"],
            tool_name=tc["name"],
            tool_args=tc["args"],
            status="pending",
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        approval_out = schemas.ApprovalOut.model_validate(approval)

    return {
        "conversation_id": conv.id,
        "message": schemas.MessageOut.model_validate(assistant_msg),
        "approval": approval_out,
    }


@router.get("/conversations", response_model=list[schemas.ConversationOut])
def list_conversations(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(models.Conversation)
        .where(models.Conversation.user_id == user.id)
        .order_by(models.Conversation.created_at.desc())
    ).scalars().all()
    return rows


@router.get("/conversations/{conversation_id}/messages", response_model=list[schemas.MessageOut])
def list_messages(
    conversation_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.get(models.Conversation, conversation_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "Conversation not found")

    rows = db.execute(
        select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at)
    ).scalars().all()
    return rows
