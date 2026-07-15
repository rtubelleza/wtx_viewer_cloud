resource "openstack_networking_secgroup_v2" "app" {
  name = var.instance_name
  description = "Ingress for the wtx viewer (${var.instance_name}): SSH + HTTP/HTTPS"
}

# SSH (22)
resource "openstack_networking_secgroup_rule_v2" "ssh" {
  security_group_id = openstack_networking_secgroup_v2.app.id
  direction = "ingress"
  ethertype = "IPv4"
  protocol = "tcp"
  port_range_min = 22
  port_range_max = 22
  remote_ip_prefix = var.ssh_ingress_cidr
  description = "SSH"
}

# HTTP (80); certbot's ACME challenge done on port 80
resource "openstack_networking_secgroup_rule_v2" "http" {
  security_group_id = openstack_networking_secgroup_v2.app.id
  direction = "ingress"
  ethertype = "IPv4"
  protocol = "tcp"
  port_range_min = 80
  port_range_max = 80
  remote_ip_prefix = "0.0.0.0/0"
  description = "HTTP"
}

# HTTPS (443)
resource "openstack_networking_secgroup_rule_v2" "https" {
  security_group_id = openstack_networking_secgroup_v2.app.id
  direction = "ingress"
  ethertype = "IPv4"
  protocol = "tcp"
  port_range_min = 443
  port_range_max = 443
  remote_ip_prefix = var.app_https_cidr
  description = "HTTPS"
}
