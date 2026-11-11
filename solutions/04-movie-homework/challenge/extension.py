from pydantic import BaseModel, Field
from main import app, get_movie

class Guess(BaseModel):
    title: str=Field(min_length=1,max_length=200)

@app.post("/movie/guess")
def guess(body: Guess):
    expected=get_movie()["title"].strip().casefold()
    return {"correct":body.title.strip().casefold()==expected}
