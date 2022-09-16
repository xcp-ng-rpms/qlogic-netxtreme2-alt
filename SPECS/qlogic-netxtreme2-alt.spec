%define vendor_name Qlogic
%define vendor_label qlogic
%define driver_name netxtreme2

%if %undefined kernel_version
%define kernel_version %(uname -r)
%endif
%if %undefined module_dir
%define module_dir override
%endif
%if %undefined modules_suffix
%define modules_suffix modules
%endif

%define build_defs BNX2FC_KERNEL_OVERRIDE=1 BNX2FC_SUP=-DXENSERVER DISTRO=Citrix

%define name_orig %{vendor_label}-%{driver_name}

Summary: Qlogic NetXtreme II iSCSI, 1-Gigabit and 10-Gigabit ethernet drivers
Name: %{name_orig}-alt
Version: 7.14.76
Release: 3%{?dist}
License: GPL
Group: System Environment/Kernel
BuildRequires: kernel-devel, git
BuildRequires: gcc
BuildRequires: kernel-devel
BuildRequires: bc
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

# Obsolete the old module subpackage
Obsoletes: qlogic-netxtreme2-alt-4.19.0+1-modules

#Source taken from a SRPM at http://ldriver.qlogic.com/driver-srpms/netxtreme2/
Source: %{driver_name}-%{version}.tar.gz

# XCP-ng patches
Patch1000: qlogic-netxtreme2-7.14.69-install-into-dedicated-dir.XCP-ng.patch 
Patch1001: qlogic-netxtreme2-Fix-NULL-pointer-dereference-in-bnx2x_del_all_vlans.backport.patch

%description
This package contains the Qlogic NetXtreme II iSCSI (bnx2i), 1-Gigabit (bnx2) and 10-Gigabit (bnx2x) ethernet drivers.

%prep
%autosetup -p1 -n %{driver_name}-%{version}

%build
%{?cov_wrap} %{__make} KVER=%{kernel_version} %{build_defs}

%install
%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
echo 'options bnx2x num_vfs=0' > %{name_orig}.conf
%{__install} %{name_orig}.conf %{buildroot}%{_sysconfdir}/modprobe.d
%{__mkdir_p} $RPM_BUILD_ROOT%{_mandir}/man4
%{__install} -d %{buildroot}/lib/modules/%{kernel_version}/%{module_dir}
%{?cov_wrap} %{__make} PREFIX=$RPM_BUILD_ROOT KVER=%{kernel_version} %{build_defs} BCMMODDIR=/lib/modules/%{kernel_version}/%{module_dir} DRV_DIR=%{module_dir} DEPMOD=/bin/true install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+wx

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
/lib/modules/%{kernel_version}/*/*.ko
%exclude /etc/depmod.d/bnx2x.conf
%exclude %{_mandir}/man4/*

%changelog
* Fri Sep 16 2022 Samuel Verschelde <stormi-xcp@ylix.fr> - 7.14.76-3
- Rebuild for XCP-ng 8.3

* Wed Mar 10 2021 Samuel Verschelde <stormi-xcp@ylix.fr> - 7.14.76-2
- Merge the two RPMs into one for easier uninstallation
- Obsoletes qlogic-netxtreme2-alt-4.19.0+1-modules

* Thu Feb 25 2021 Samuel Verschelde <stormi-xcp@ylix.fr> - 7.14.76-1
- Updated to version 7.14.76

* Tue Sep 08 2020 Rushikesh Jadhav <rushikesh7@gmail.com> - 7.14.69-1
- Updated to version 7.14.69

* Wed Aug 19 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 7.14.63-3
- Rebuild for XCP-ng 8.2

* Wed Feb 12 2020 Samuel Verschelde <stormi-xcp@ylix.fr> - 7.14.63-2
- Version 7.14.63
- Add qlogic-netxtreme2-Fix-NULL-pointer-dereference-in-bnx2x_del_all_vlans.backport.patch

* Tue Dec 20 2018 Deli Zhang <deli.zhang@citrix.com> - 7.14.53-1
- CP-30078: Upgrade netXtreme2 driver to version 7.14.53

* Mon Oct 23 2017 Simon Rowe <simon.rowe@citrix.com> - 7.14.29.1-1
- UPD-107: update netxtreme2 driver to 7.14.29.1 (QL-643)
