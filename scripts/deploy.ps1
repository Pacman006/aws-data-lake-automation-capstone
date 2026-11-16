# Windows PowerShell equivalent of deploy.sh.
$ErrorActionPreference = 'Stop'
$region = if ($env:AWS_REGION) { $env:AWS_REGION } else { 'ap-south-1' }
$stage = if ($env:ENVIRONMENT) { $env:ENVIRONMENT } else { 'dev' }
$prefix = if ($env:PROJECT_PREFIX) { $env:PROJECT_PREFIX } else { 'datasoftlake' }
$stack = if ($env:STACK_NAME) { $env:STACK_NAME } else { "$prefix-$stage" }

aws sts get-caller-identity
if ($LASTEXITCODE -ne 0) { throw 'Check your AWS CLI credentials.' }
Write-Host "Deploying $stack to $region. AWS charges may apply."
$answer = Read-Host 'Type DEPLOY to continue'
if ($answer -cne 'DEPLOY') { Write-Host 'Cancelled.'; exit 1 }
sam build --template-file cloudformation/template.yaml --build-dir .aws-sam/build
if ($LASTEXITCODE -ne 0) { throw 'SAM build failed.' }
sam deploy --template-file .aws-sam/build/template.yaml --stack-name $stack --region $region --capabilities CAPABILITY_IAM --resolve-s3 --parameter-overrides "ProjectName=$prefix" "Environment=$stage" --confirm-changeset --no-fail-on-empty-changeset
if ($LASTEXITCODE -ne 0) { throw 'SAM deployment failed.' }
aws cloudformation describe-stacks --stack-name $stack --region $region --query 'Stacks[0].Outputs' --output table
