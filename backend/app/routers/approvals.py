from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app import models, schemas

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/{approval_id}/approve", response_model=schemas.ApprovalOut)
def approve(
    approval_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ap = db.get(models.PendingApproval, approval_id)
    if not ap or ap.user_id != user.id:
        raise HTTPException(404, "Approval not found")
    if ap.status != "pending":
        raise HTTPException(400, f"Already {ap.status}")

    # Execute tool
    if ap.tool_name == "create_task":
        task = models.Task(
            user_id=user.id,
            conversation_id=ap.conversation_id,
            title=ap.tool_args.get("title", "Untitled"),
            description=ap.tool_args.get("description"),
            status="pending",
        )
        db.add(task)

    # Write tool result message so history stays coherent
    tool_msg = models.Message(
        conversation_id=ap.conversation_id,
        role="tool",
        content=f"Approved: {ap.tool_name} with args {ap.tool_args}",
        tool_calls=None,
	tool_call_id=ap.tool_call_id,
    )
    db.add(tool_msg)

    ap.status = "approved"
    db.commit()
    db.refresh(ap)
    return ap


@router.post("/{approval_id}/reject", response_model=schemas.ApprovalOut)
def reject(
    approval_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ap = db.get(models.PendingApproval, approval_id)
    if not ap or ap.user_id != user.id:
        raise HTTPException(404, "Approval not found")
    if ap.status != "pending":
        raise HTTPException(400, f"Already {ap.status}")

    ap.status = "rejected"
    tool_msg = models.Message(
        conversation_id=ap.conversation_id,
        role="tool",
        content=f"Rejected: {ap.tool_name}",
        tool_calls=None,
	tool_call_id=ap.tool_call_id,
    )
    db.add(tool_msg)
    db.commit()
    db.refresh(ap)
    return ap
