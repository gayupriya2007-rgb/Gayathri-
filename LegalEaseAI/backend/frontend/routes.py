class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    dates: str
    