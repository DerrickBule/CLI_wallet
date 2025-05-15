docker build -t  tokentrace-postgres .
docker run -d --name tokentrace-postgres -p 5432:5432 tokentrace-postgres