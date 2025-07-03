module "template_files" {
  source   = "hashicorp/dir/template"
  base_dir = "../website/build"
}

data "terraform_remote_state" "gcs" {
  backend = "gcs"

  config = {
    bucket = "calitp-prod-gcp-components-tfstate"
    prefix = "cal-itp-data-infra/gcs"
  }
}