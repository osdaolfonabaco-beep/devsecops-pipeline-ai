#
# infra/main.tf
#
# Terraform configuration for a simple S3 bucket.
# This file contains an **INTENTIONAL VULNERABILITY** for
# the DevSecOps AI pipeline to detect.
#
# WARNING: DO NOT APPLY THIS CONFIGURATION IN A PRODUCTION ENVIRONMENT.
#

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "data_bucket" {
  # This bucket name is for demo purposes and will likely conflict.
  bucket = "mi-bucket-de-datos-super-secreto-12345"

  #
  # --- 🔴 INTENTIONAL VULNERABILITY: Public S3 Bucket ---
  # WARNING: The 'public-read' ACL makes this bucket's contents
  # accessible to the entire internet. This is a critical
  # security misconfiguration our AI scanner is designed to find.
  #
  acl = "public-read"
}
