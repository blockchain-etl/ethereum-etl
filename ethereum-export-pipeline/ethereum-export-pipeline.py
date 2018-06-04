from ethereumexportpipeline.utils import split_to_batches
from troposphere import Template, Parameter, Ref
from troposphere.datapipeline import Pipeline, PipelineTag, PipelineObject, ObjectField, ParameterObject, \
    ParameterObjectAttribute

t = Template()

# CloudFormation version
t.add_version('2010-09-09')

t.add_description('Ethereum ETL Export CloudFormation Stack')

# Parameters

S3Bucket = t.add_parameter(Parameter(
    "S3Bucket",
    Description="S3 bucket where CSV files will be uploaded",
    Type="String",
    Default="example.com"
))

Command = t.add_parameter(Parameter(
    "Command",
    Description="Shell command that will be executed on workers",
    Type="String",
    Default="cd /home/ec2-user/ethereum-etl && bash -x export_all.sh -s $1 -e $2 -b $3 -i /home/ec2-user/.ethereum/geth.ipc -o ${OUTPUT1_STAGING_DIR}"
))

# The first million blocks are in a single partition
# The next 3 million blocks are in 100k partitions
# The next 1 million blocks are in 10k partitions
# Note that there is a limit in Data Pipeline on the number of objects that can be increased in Support Center
# https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-limits.html
export_jobs = [(0, 999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(1000000, 1999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(2000000, 2999999, 1000000)] + \
              [(start, end, 100000) for start, end in split_to_batches(3000000, 3999999, 1000000)] + \
              [(start, end, 10000) for start, end in split_to_batches(4000000, 4999999, 10000)]

t.add_resource(Pipeline(
    "EthereumETLPipeline",
    Name="EthereumETLPipeline",
    Description="Ethereum ETL Export Pipeline",
    PipelineTags=[PipelineTag(Key='Name', Value='ethereum-etl-pipeline')],
    ParameterObjects=[
        ParameterObject(Id='myS3Bucket', Attributes=[
            ParameterObjectAttribute(Key='type', StringValue='String'),
            ParameterObjectAttribute(Key='description', StringValue='S3 bucket'),
            ParameterObjectAttribute(Key='default', StringValue=Ref(S3Bucket)),
        ]),
        ParameterObject(Id='myShellCmd', Attributes=[
            ParameterObjectAttribute(Key='type', StringValue='String'),
            ParameterObjectAttribute(Key='description', StringValue='S3 bucket'),
            ParameterObjectAttribute(Key='default', StringValue=Ref(Command)),
        ])
    ],
    PipelineObjects=
    [PipelineObject(
        Id='Default',
        Name='Default',
        Fields=[
            ObjectField(Key='type', StringValue='Default'),
            ObjectField(Key='failureAndRerunMode', StringValue='cascade'),
            ObjectField(Key='scheduleType', StringValue='ondemand'),
            ObjectField(Key='role', StringValue='DataPipelineDefaultRole'),
            ObjectField(Key='pipelineLogUri', StringValue='s3://#{myS3Bucket}/'),

        ]
    )] +
    [PipelineObject(
        Id='ExportActivity_{}_{}_{}'.format(start, end, batch),
        Name='ExportActivity_{}_{}_{}'.format(start, end, batch),
        Fields=[
            ObjectField(Key='type', StringValue='ShellCommandActivity'),
            ObjectField(Key='command', StringValue='#{myShellCmd}'),
            ObjectField(Key='scriptArgument', StringValue=str(start)),
            ObjectField(Key='scriptArgument', StringValue=str(end)),
            ObjectField(Key='scriptArgument', StringValue=str(batch)),
            ObjectField(Key='workerGroup', StringValue='ethereum-etl'),
            ObjectField(Key='output', RefValue='S3OutputLocation'),
            ObjectField(Key='stage', StringValue='true')

        ]
    ) for start, end, batch in export_jobs] +
    [PipelineObject(
        Id='S3OutputLocation',
        Name='S3OutputLocation',
        Fields=[
            ObjectField(Key='type', StringValue='S3DataNode'),
            ObjectField(Key='directoryPath', StringValue='s3://#{myS3Bucket}/ethereum-etl/export-pipeline')

        ]
    )]
))

# Write json template to file

with open('ethereum-export-pipeline.template', 'w+') as output_file:
    output_file.write(t.to_json())
