from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from typing import List

from connectors.fetchers import BaseFetcher


@dataclass

class RawProgram:
    """kaynaktan alınan raw program bilgisi."""
    program_id: str
    title: str
    agency: str
    source: str
    category: str
    region: str
    description: str
    deadline: Optional[datetime] = None
    official_url: Optional[str] = None


    #opsiyonel alanlar
    sub_category: Optional[str] = None
    support_type: Optional[str] = None      
    max_amount_try: Optional[float] = None
    max_amount_usd: Optional[float] = None
    conditions_summary: Optional[str] = None
    application_status: Optional[str] = None
    start_date: Optional[datetime] = None
    min_employee: Optional[int] = None
    max_employee: Optional[int] = None
    founded_after: Optional[datetime] = None


class BaseConnector(ABC):
    """Tüm connectorlar için temel sınıf.
      Her connector bu sınıftan türetilmeli ve gerekli metodları implement etmelidir."""

    def __init__(self, fetcher: BaseFetcher):
        self.fetcher = fetcher


    @abstractmethod
    async def extract(self) -> list[RawProgram]:
        """Kaynaktan ham program verilerini çeker ve RawProgram listesi döner."""    
        
        pass

