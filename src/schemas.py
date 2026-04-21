from pydantic import BaseModel, Field


class TavilySummarizeItem(BaseModel):
  title: str = Field(description = "Title of the article")
  link: str = Field(description = "Link to the article")
  snippet: str = Field(description = "Snippet of the article")
  date: str = Field(description = "Publication date of the article")
  source: str = Field(description = "Source of the article")