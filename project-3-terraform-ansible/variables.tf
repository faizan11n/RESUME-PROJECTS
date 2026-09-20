variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-west-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name to register the SSH key pair under in AWS"
  type        = string
  default     = "terraform-demo-key"
}

variable "public_key_path" {
  description = "Path to the local SSH public key file"
  type        = string
  default     = "~/.ssh/terraform-key.pub"
}

variable "private_key_path" {
  description = "Path to the local SSH private key file (used by Ansible)"
  type        = string
  default     = "~/.ssh/terraform-key"
}
