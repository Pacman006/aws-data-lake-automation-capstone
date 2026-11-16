#!/usr/bin/env bash
# Deploy the CloudFormation/SAM pilot. Review AWS charges and IAM changes first.
set -euo pipefail

REGION="${AWS_REGION:-ap-south-1}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
PREFIX="${PROJECT_PREFIX:-datasoftlake}"
STACK_NAME="${STACK_NAME:-${PREFIX}-${ENVIRONMENT}}"

command -v sam >/dev/null || { echo 'Install AWS SAM CLI first.' >&2; exit 1; }
command -v aws >/dev/null || { echo 'Install AWS CLI v2 first.' >&2; exit 1; }
aws sts get-caller-identity
printf '\nStack: %s | Region: %s | Environment: %s\n' "$STACK_NAME" "$REGION" "$ENVIRONMENT"
printf 'This deployment creates BILLABLE AWS resources. Continue? Type DEPLOY: '
read -r confirmation
[[ "$confirmation" == "DEPLOY" ]] || { echo 'Cancelled.'; exit 1; }

sam build --template-file cloudformation/template.yaml --build-dir .aws-sam/build
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --capabilities CAPABILITY_IAM \
  --resolve-s3 \
  --parameter-overrides "ProjectName=${PREFIX}" "Environment=${ENVIRONMENT}" \
  --confirm-changeset \
  --no-fail-on-empty-changeset

aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs' --output table
