# infra/main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "mi-bucket-de-datos-super-secreto-12345"

  # ¡MALA PRÁCTICA DE SEGURIDAD!
  # Esto hace que el bucket sea legible por todo el mundo.
  acl = "public-read" 
}
