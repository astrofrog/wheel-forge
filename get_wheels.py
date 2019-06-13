import os
import tarfile
import tempfile

import requests

BUILDS_URL = 'https://dev.azure.com/{pipeline_id}/_apis/build/builds'
ARTIFACTS_URL = BUILDS_URL + '/{build_id}/artifacts'


def download_wheels(pipeline_id, build_id=None):

    # Get build_id if needed

    if build_id is None:
        r = requests.get(BUILDS_URL.format(pipeline_id=pipeline_id))
        build_id = r.json()['value'][0]['id']

    print(f'Fetching wheels for build {build_id} of {pipeline_id}')

    # Get list of artifacts

    artifacts_url = ARTIFACTS_URL.format(pipeline_id=pipeline_id, build_id=build_id)
    r = requests.get(artifacts_url)
    artifacts = r.json()['value']

    # Retrieve artifacts

    tmpdir = tempfile.mkdtemp()
    print(f'Downloading {len(artifacts)} artifacts to {tmpdir}')

    for artifact in artifacts:

        filename = artifact['name']

        params = {'artifactName': filename,
                  'fileName': filename,
                  'fileId': artifact['resource']['data'],
                  'api-version': '5.0-preview.5'}

        artifact_ref = requests.get(artifacts_url, params).json()

        params['fileId'] = artifact_ref['items'][0]['blob']['id']

        artifact = requests.get(artifacts_url, params)

        with open(os.path.join(tmpdir, filename), 'wb') as f:
            f.write(artifact.content)

        print(f' -> downloaded {filename}')

    print(f'Extracting wheels to current directory')

    for artifact_file in os.listdir(tmpdir):

        tar = tarfile.open(os.path.join(tmpdir, artifact_file))
        tar.extractall('.')


if __name__ == '__main__':
    download_wheels('astropy-project/wheel-forge')
