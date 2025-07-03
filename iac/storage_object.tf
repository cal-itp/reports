resource "google_storage_bucket_object" "reports" {
  for_each     = module.template_files.files
  bucket       = data.terraform_remote_state.gcs.outputs.google_storage_bucket_calitp-reports_name
  name         = each.key
  content_type = each.value.content_type
  source       = each.value.source_path
  content      = each.value.content
}
