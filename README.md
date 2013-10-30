=========================
SELinux Modules for Kolab
=========================

These packages provide SELinux modules for Kolab components:

**kolab-saslauthd**

    The Kolab Groupware integrated, multi-domain capable SASL Authentication
    daemon, mimicing the SASL policies from serefpolicy-contrib.

Remember to set **httpd_can_network_connect**:

    # :command:`setsebool -P httpd_can_network_connect 1`
