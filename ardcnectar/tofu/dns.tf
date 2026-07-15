# lookup project allocated zone
data "openstack_dns_zone_v2" "zone" {
  name = var.target_zone
}

# A record pointing to viewer domain
resource "openstack_dns_recordset_v2" "app" {
  zone_id = data.openstack_dns_zone_v2.zone.id
  name = var.app_domain # full domain with prefix and trailing dot
  type = "A"
  ttl = var.dns_ttl
  records = [local.vm_ip]
}
