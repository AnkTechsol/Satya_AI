from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import select
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.policy import Policy
from ..schemas.policy import PolicyCreate, PolicyRead, PolicyUpdate
from ..core.interceptor import verify_satya_key

router = APIRouter(prefix="/v1/policies", tags=["Policies"], dependencies=[Depends(verify_satya_key)])

@router.post("", response_model=PolicyRead)
async def create_policy(policy_in: PolicyCreate, db: AsyncSession = Depends(get_db)):
    db_policy = Policy(**policy_in.model_dump())
    db.add(db_policy)
    await db.commit()
    await db.refresh(db_policy)
    return db_policy

@router.get("", response_model=List[PolicyRead])
async def list_policies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy))
    policies = result.scalars().all()
    return policies

@router.get("/{policy_id}", response_model=PolicyRead)
async def get_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/{policy_id}", response_model=PolicyRead)
async def update_policy(policy_id: str, policy_in: PolicyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = policy_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(policy, key, value)

    await db.commit()
    await db.refresh(policy)
    return policy

@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.is_active = False # Soft delete
    await db.commit()
    return {"message": "Policy deactivated"}

@router.post("/{policy_id}/attach/{agent_id}")
async def attach_policy(policy_id: str, agent_id: str, db: AsyncSession = Depends(get_db)):
    from ..models.agent import Agent
    # Verify policy exists
    p_result = await db.execute(select(Policy).where(Policy.id == policy_id))
    if not p_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Policy not found")

    # Verify agent exists
    a_result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = a_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Attach
    current_policies = list(agent.policies)
    if policy_id not in current_policies:
        current_policies.append(policy_id)
        # SQLAlchemy JSON columns sometimes need reassignment to trigger update
        agent.policies = current_policies
        await db.commit()

    return {"message": "Policy attached to agent"}
