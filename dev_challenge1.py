import os
import sys
import glob
import captools.api
import json
from captools.api import Client

api_token = os.environ.get("Captricity_API_Token", None)
print api_token
print

# For this example and in future examples, client refers to a Client object from captools.api.Client 
client = Client(api_token)

# The Batch resource is a collection of Batch Files. 
# The first step to digitizing your forms is to create a new batch:

# batch = client.create_batches({'name': "Customer Survey 2014"})
# print batch['id']


batches = client.read_batches()
batch_id = filter(lambda x: x['name'] == 'Customer Survey 2014', batches).pop()['id']
print batch_id
print

# batch = client.read_batch(batch_id)
# print 'Batch: ', batch['name'], '-', batch['id']
# print


# To digitize a batch, you need a Document to serve as the blank template form.
# Documents can only be defined via the Captricity Web UI. Once your Document is created, 
# you can use the Captricity API to get the id of your document:

documents = client.read_documents()


# Select the id of the template you would like to use. -- Form_012rev1 -- created on 10.17.14
document_id = filter(lambda x: x['name'] == 'Form_012rev1', documents).pop()['id']
print 'Template ID: ', document_id
print

sys.exit()
# Once you have the id of the document, you can assign the document to the batch. 
# You can also do this step after you have uploaded your files.

client.update_batch(batch_id, { 'documents': document_id })


# Loop over files to upload:

for img in glob.glob('scanned_images/*.pdf'):
    if os.path.isfile(img):
        f = open(img, 'rb')
        print f.name+', '+str(os.fstat(f.fileno()).st_size)
        batch_file = client.create_batch_files(batch_id, {'uploaded_file': f})

print
batch_files = client.read_batch_files(batch_id)
for bf in batch_files:
    print bf['file_name'], '-', bf['id']
print


# Once you have uploaded all the forms you would like to digitize, the next step 
# is to submit your Batch for processing.  Before you submit your Batch, you should 
# ensure that it is ready to be submitted. Use the Batch Readiness resource to 
# detect any problems in your completed forms or templates.

print client.read_batch_readiness(batch_id)
print

# Check the errors property to ensure your Batch can be submitted. 
# There must be no errors for the batch to go through. 
# The other properties of this resource give you details on corrective action 
#   if your Batch is not ready for submission.
# Batch submission charges your Captricity account. 
# Check the pricing details of your Batch using the Batch Price resource:

batch_price = client.read_batch_price(batch_id)


# The total_batch_cost_in_fields property is the price of digitizing the batch in fields. 
# The total_user_cost_in_cents is the total charge to your account for running the Batch. 
# If you have more credit in your account than the Batch costs, total_user_cost_in_cents is 0.
# If total_user_cost_in_cents is non-zero, you must add credit to your account before you 
#   submit your Batch via the Captricity API.
# When you are ready to run your Batch, submit it by sending an HTTP POST to the 
#   Submit Batch resource. This charges your account and begins the digitization process 
#   of your Batch.

batch = client.submit_batch(batch_id, {})


# At this point, your batch will be converted into a Job. 
# You can use the related_job_id property of the Batch to look up the Job resource.

job = client.read_job(job_id)


# Digitization time varies between a few minutes to a few hours depending on your Job's size. 
# You can track the progress of your Job using the percent_completed property of the Job resource.
# Once your Job is complete, you can use the Captricity API to extract your results.
# If you are interested in the results from a certain Instance Set, you can pull the digitized 
#   data for just the Shreds in that Instance Set. 
# First, find your Instance Set's id by listing all the Instance Sets in the Job:

instance_sets = client.read_instance_sets(job_id)


# Once you have found the id of your Instance Set, you can then list all the Shreds 
# in that Instance Set using the Instance Set Shreds resource:

client.read_instance_set_shreds(instance_sets[0]['id'])

# The result of the digitization is in the best_estimate property of each Shred.
# If you'd like the whole dataset, grab the CSV export from the Job Results CSV resource.

csv_out = client.read_job_results_csv(job_id)

print csv_out


