configure terminal
telemetry ietf subscription 17
 stream yang-push
 filter xpath /if:interfaces-state/interface[name="GigabitEthernet1"]/statistics/in-octets
 update-policy periodic 1000
 encoding encode-kvgpb
 source-vrf clab-mgmt
 receiver ip address 172.20.20.1 57000 protocol grpc-tcp
end

show telemetry ietf subscription 17 detail
ping vrf clab-mgmt 172.20.20.1 source GigabitEthernet1

<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="3" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>]]>]]><rpc message-id="4" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
     xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target><running/></target>
    <config>
      <mdt-config-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg">
        <mdt-subscription nc:operation="replace">
          <subscription-id>18</subscription-id>
          <base>
            <stream>yang-push</stream>
            <encoding>encode-kvgpb</encoding>
            <source-vrf>clab-mgmt</source-vrf>
            <period>1000</period>
                        <xpath>/if:interfaces-state/interface[name="GigabitEthernet1"]/statistics/in-octets</xpath>
          </base>
          <mdt-receivers>
            <address>172.20.20.1</address>
            <port>57000</port>
            <protocol>grpc-tcp</protocol>
          </mdt-receivers>
        </mdt-subscription>
      </mdt-config-data>
    </config>
  </edit-config>
</rpc>]]>]]>