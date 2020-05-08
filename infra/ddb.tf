resource "aws_dynamodb_table" "poe_api_export_cache" {
  name         = "poe_item_alerts_characters"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "league_name"
  range_key    = "character_name"

  attribute {
    name = "league_name"
    type = "S"
  }
  attribute {
    name = "character_name"
    type = "S"
  }
}

