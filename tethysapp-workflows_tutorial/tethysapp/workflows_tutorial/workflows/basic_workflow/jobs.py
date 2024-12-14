from pathlib import Path
from ..utilities import safe_str, get_condor_env

REQUEST_CPUS_PER_JOB = 1
JOB_EXECUTABLES_DIR = Path(__file__).parent / 'job_executables'


def build_jobs_callback(condor_workflow):
    """
    Define the Condor Jobs for the run step.

    Returns:
        list<dicts>: Condor Job dicts, one for each job.
    """
    jobs = []
    condor_env = get_condor_env()
    workflow = condor_workflow.tethys_workflow

    # Get the selected scenarios
    points_step = workflow.get_step_by_name('Point In Boundary Step')
    points_geometry = points_step.get_parameter('geometry')

    # Create one job per point
    for idx, point in enumerate(points_geometry.get('features', [])):
        # Set up the job for the generic job
        executable = 'run_generic_job.py'
        point_name = point.get('properties', {}).get('point_name', f'point_{idx + 1}')
        job_name = f'run_{safe_str(point_name)}'
        output_filename = f'{job_name}_out.json'

        job = {
            'name': job_name,
            'condorpy_template_name': 'vanilla_transfer_files',
            'category': 'generic_job',
            'remote_input_files': [str(JOB_EXECUTABLES_DIR / executable), ],
            'attributes': {
                'executable': executable,
                'arguments': [point_name, idx, output_filename],
                'transfer_input_files': [f'../{executable}', ],
                'transfer_output_files': [output_filename, ],
                'environment': condor_env,
                'request_cpus': REQUEST_CPUS_PER_JOB
            }
        }

        # Add to workflow jobs
        jobs.append(job)

    return jobs