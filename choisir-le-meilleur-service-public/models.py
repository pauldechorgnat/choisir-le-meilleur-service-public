from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


def parse_french_date(value):
    return datetime.strptime(value, "%d/%m/%Y").date()


class ShortOffering(BaseModel):
    reference: str = Field(..., alias="Référence")
    job_title: str = Field(..., alias="Intitulé du poste")
    organization: str = Field(..., alias="Organisme de rattachement")
    first_publication_date: str = Field(..., alias="Date de première publication")


class Offering(ShortOffering):
    languages: Optional[str] = Field(None, alias="Langues")
    job_type: Optional[str] = Field(None, alias="Nature de l'emploi")
    specialization: Optional[str] = Field(None, alias="Spécialisation")
    employer: Optional[str] = Field(None, alias="Employeur")
    category: Optional[str] = Field(None, alias="Catégorie")
    management: Optional[str] = Field(None, alias="Management")
    full_time: Optional[str] = Field(None, alias="Temps Plein")
    remote_work: Optional[str] = Field(None, alias="Télétravail")
    job_duration: Optional[str] = Field(None, alias="Durée du poste")
    job_status: Optional[str] = Field(None, alias="Statut du poste")
    education_level: Optional[str] = Field(None, alias="Niveau d'études")
    contract_duration: Optional[str] = Field(None, alias="Durée du contrat")
    contract_type: Optional[str] = Field(None, alias="Nature de contrat")
    location: Optional[str] = Field(None, alias="Lieu d'affectation")
    location_without_geo: Optional[str] = Field(None, alias="Lieu d'affectation (sans géolocalisation)")
    job_location: Optional[str] = Field(None, alias="Localisation du poste")
    jo_publication: Optional[str] = Field(None, alias="Avis de vacances au JO")
    skills_required: Optional[str] = Field(None, alias="Compétences attendues")
    documents_required: Optional[str] = Field(None, alias="Documents à transmettre")
    job_vacancy_date: Optional[str] = Field(None, alias="Date de vacance de l'emploi")
    min_experience_level: Optional[str] = Field(None, alias="Niveau d'expérience min. requis")
    default_publication_end_date: Optional[str] = Field(None, alias="Date de fin de publication par défaut")
    default_publication_start_date: Optional[str] = Field(None, alias="Date de début de publication par défaut")
    levels: Optional[str] = Field(None, alias="Niveaux")
    versant: Optional[str] = Field(None, alias="Versant")


def format_data(raw_data: dict) -> dict:
    return Offering(**raw_data).model_dump()
