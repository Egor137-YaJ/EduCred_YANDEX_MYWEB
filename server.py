import os
from flask import Flask
from flask_restful import Api
from data import db_session


app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
db_session.global_init("db/EduCred_data.db")

api = Api(app, catch_all_404s=True)


def main():
    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:job_id>', methods=['GET', 'PUT', 'DELETE'])



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# My web: https://precious-fluoridated-muskox.glitch.me/
# create git with only this directory on git. just files of that github
# My Projects: https://glitch.com/dashboard?group=owned&sortColumn=boost&sortDirection=DESC&page=1&showAll=false&filterDomain=