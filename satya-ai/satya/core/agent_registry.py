from typing import List, Optional
from sqlalchemy import select
from ..database import AsyncSessionLocal
from ..models.agent import Agent
from ..models.policy import Policy
from ..schemas.agent import AgentCreate, AgentRead, AgentUpdate
from ..schemas.policy import PolicyRead

class AgentRegistry:
    """Registry for managing agents and their attached policies."""

    async def register_agent(self, agent_data: AgentCreate) -> AgentRead:
        async with AsyncSessionLocal() as session:
            db_agent = Agent(**agent_data.model_dump())
            session.add(db_agent)
            await session.commit()
            await session.refresh(db_agent)
            return AgentRead.model_validate(db_agent, from_attributes=True)

    async def get_agent(self, agent_id: str) -> Optional[AgentRead]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Agent).where(Agent.agent_id == agent_id))
            db_agent = result.scalar_one_or_none()
            if db_agent:
                return AgentRead.model_validate(db_agent, from_attributes=True)
            return None

    async def list_agents(self) -> List[AgentRead]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Agent))
            agents = result.scalars().all()
            return [AgentRead.model_validate(a, from_attributes=True) for a in agents]

    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> Optional[AgentRead]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Agent).where(Agent.agent_id == agent_id))
            db_agent = result.scalar_one_or_none()
            if not db_agent:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(db_agent, key, value)

            await session.commit()
            await session.refresh(db_agent)
            return AgentRead.model_validate(db_agent, from_attributes=True)

    async def get_policies_for_agent(self, agent_id: str) -> List[PolicyRead]:
        """Returns the fully hydrated policy objects attached to an agent."""
        agent = await self.get_agent(agent_id)
        if not agent or not agent.policies:
            return []

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Policy).where(Policy.id.in_(agent.policies)))
            policies = result.scalars().all()
            return [PolicyRead.model_validate(p, from_attributes=True) for p in policies]
