resource "aws_dynamodb_table" "poe_api_export_cache" {
  name         = "poe_item_alerts_characters"
  billing_mode = "PAY_PER_REQUEST"
  range_key    = "account_name"
  hash_key     = "character_name"

  attribute {
    name = "character_name"
    type = "S"
  }

  attribute {
    name = "account_name"
    type = "S"
  }
}

