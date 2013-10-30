%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp 2>/dev/null)}
%if "%{_selinux_policy_version}" != ""
Requires:      selinux-policy >= %{_selinux_policy_version}
%endif

%global selinux_types %(%{__awk} '/^#[[:space:]]*SELINUXTYPE=/,/^[^#]/ { if ($3 == "-") printf "%s ", $2 }' /etc/selinux/config 2>/dev/null)
%global selinux_variants %([ -z "%{selinux_types}" ] && echo mls targeted || echo %{selinux_types})

Name:               kolab-selinux
Version:            0.0.1
Release:            1%{?dist}
Summary:            SELinux modules for Kolab Groupware

Group:              System Environment/Daemons
License:            GPLv3+
URL:                http://kolab.org/about/selinux

Source0:            kolab.fc
Source1:            kolab.te

Requires:           selinux-policy

Requires(post):     /sbin/fixfiles
Requires(post):     /sbin/restorecon
Requires(post):     /usr/sbin/semodule

Requires(postun):   /sbin/fixfiles
Requires(postun):   /sbin/restorecon
Requires(postun):   /usr/sbin/semodule

BuildRequires:      checkpolicy
BuildRequires:      hardlink
BuildRequires:      selinux-policy-devel
BuildRequires:      /usr/share/selinux/devel/policyhelp

%description
Security-Enhanced Linux modules for Kolab Groupware

%prep
mkdir kolab
cp -p %{SOURCE0} %{SOURCE1} kolab

%build
for module in kolab; do
    pushd $module
    for selinuxvariant in %{selinux_variants}; do
        make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
        mv $module.pp $module.pp.${selinuxvariant}
        make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
    done
    popd
done

%install
for module in kolab; do
    for selinuxvariant in %{selinux_variants}; do
        install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
        install -p -m 644 $module/$module.pp.${selinuxvariant} \
            %{buildroot}%{_datadir}/selinux/${selinuxvariant}/$module.pp
    done
done

/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux

%post
for module in kolab; do
    for selinuxvariant in %{selinux_variants}; do
        /usr/sbin/semodule -s ${selinuxvariant} -i \
            %{_datadir}/selinux/${selinuxvariant}/$module.pp &> /dev/null || :
    done
    /sbin/fixfiles -R $module restore || :
done

/sbin/restorecon -R %{_initrddir} || :

%postun
if [ $1 -eq 0 ] ; then
    for module in kolab; do
        for selinuxvariant in %{selinux_variants}; do
            /usr/sbin/semodule -s ${selinuxvariant} -r $module &> /dev/null || :
        done

        /sbin/fixfiles -R $module restore || :
    done
fi

%files
%defattr(-,root,root,0755)
%doc kolab/*
%{_datadir}/selinux/*/*.pp

%changelog
* Tue Oct 29 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.0.1-1
- First package

