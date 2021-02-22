import requests
import os
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SelectField

from werkzeug.utils import secure_filename

from auth import generate_jwt
from orgPolicies import list_policies

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['UPLOAD_PATH'] = '/tmp'

sa_email_address = "mm-demo-test-org-sa@skyuk-cec-org-policy-demo-mm.iam.gserviceaccount.com"
gw_service_name = "skyuk-cec-org-policy-demo-mm"
gw_url = "https://org-policy-management-gw-54tubeme.ew.gateway.dev/policy"


class Form(FlaskForm):
    constraints = SelectField('constraints', choices=[])


@app.route('/')
def home():
    return redirect(url_for("index"))


@app.route('/index', methods=['GET', 'POST'])
def index():
    form = Form()
    form.constraints.choices = [prj for prj in list_policies(project=gw_service_name)]
    if request.method == 'GET':
        return render_template('index.html', form=form)
    else:
        if 'submit' in request.form:
            uploaded_file = request.files['json_file']
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            json_path = os.path.abspath(f'/tmp/{filename}')
            try:
                access_token = generate_jwt(sa_keyfile=json_path, sa_email=sa_email_address,
                                            audience=gw_service_name)
                body = dict(constraint=request.form.to_dict()['constraints'], project=request.form.to_dict()['project'],
                            start=request.form.to_dict()['start'], end=request.form.to_dict()['end'])
                headers = {
                    'Authorization': f"Bearer {access_token}",
                    'Accept': 'application/json'
                }
                publish = requests.post(url=gw_url,
                                        headers=headers, json=body)
                response = publish.json()
                os.remove(os.path.abspath(f'/tmp/{filename}'))
                print(response)
                return render_template('index.html', form=form,
                                       content=f"the project {request.form.to_dict()['project']} has been added to "
                                               f"the constraint {request.form.to_dict()['constraints']} - {response}...")
            except Exception as e:
                print(e)
                return render_template('index.html', form=form,
                                       content=f"Error - {e}...")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
