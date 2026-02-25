start apliakcji

uvicorn app.main:app --reload


zeby dziala merge trzeba robic
odpalic docker zeby redis server dzialal
wpisac 
celery -A app.core.celery_app worker --loglevel=info --pool=solo
potem wyslac zadanie