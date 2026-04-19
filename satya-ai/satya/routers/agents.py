from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..core.agent_registry import AgentRegistry
from ..schemas.agent import AgentCreate, AgentRead, AgentUpdate
from ..core.interceptor import verify_satya_key
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db

router = APIRouter(prefix="/v1/agents", tags=["Agents"], dependencies=[Depends(verify_satya_key)])
registry = AgentRegistry()

@router.post("", response_model=AgentRead)
async def register_agent(agent_in: AgentCreate):
    return await registry.register_agent(agent_in)

@router.get("", response_model=List[AgentRead])
async def list_agents():
    return await registry.list_agents()

@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: str):
    agent = await registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(agent_id: str, update_in: AgentUpdate):
    agent = await registry.update_agent(agent_id, update_in)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    from ..models.agent import Agent
    from sqlalchemy import select
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    # For v0.1 we might just delete or mark inactive. Let's physically delete for simplicity or remove policies
    await db.delete(agent)
    await db.commit()
    return {"message": "Agent deactivated"}
