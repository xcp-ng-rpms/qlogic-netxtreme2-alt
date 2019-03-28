%define vendor_name Qlogic
%define vendor_label qlogic
%define driver_name netxtreme2

%if %undefined kernel_version
%define kernel_version %(uname -r)
%endif

%if %undefined modules_suffix
%define modules_suffix modules
%endif

%define modules_package %{kernel_version}-%{modules_suffix}
%define build_defs BNX2FC_KERNEL_OVERRIDE=1 BNX2FC_SUP=-DXENSERVER DISTRO=Citrix

%define name_orig %{vendor_label}-%{driver_name}

Summary: Qlogic NetXtreme II iSCSI, 1-Gigabit and 10-Gigabit ethernet drivers
Name: %{name_orig}-alt
Version: 7.14.46
Release: 1%{dist}
License: GPL
Group: System Environment/Kernel
Requires: %{name}-%{modules_package} = %{version}-%{release}
#Source taken from http://ldriver.qlogic.com/driver-srpms/netxtreme2/netxtreme2-7.14.46-1.rhel7u2.src.rpm
Source: %{name_orig}-%{version}.tar.gz

# XCP-ng patches
Patch1000: qlogic-netxtreme2-7.14.46-install-into-dedicated-dir.XCP-ng.patch 

%define module_dir updates/xcp-ng/%{driver_name}-%{version}

%description
This package contains the Qlogic NetXtreme II iSCSI (bnx2i), 1-Gigabit (bnx2) and 10-Gigabit (bnx2x) ethernet drivers.

%prep
%autosetup -p1 -n %{name_orig}-%{version}

%build
%{?cov_wrap} %{__make} KVER=%{kernel_version} %{build_defs}

%install
rm -rf %{buildroot}
%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
echo 'options bnx2x num_vfs=0' > %{name_orig}.conf
%{__install} %{name_orig}.conf %{buildroot}%{_sysconfdir}/modprobe.d
%{__mkdir_p} $RPM_BUILD_ROOT%{_mandir}/man4
%{__install} -d %{buildroot}/lib/modules/%{kernel_version}/extra
%{?cov_wrap} %{__make} PREFIX=$RPM_BUILD_ROOT KVER=%{kernel_version} %{build_defs} BCMMODDIR=/lib/modules/%{kernel_version}/%{module_dir} DRV_DIR=%{module_dir} DEPMOD=/bin/true install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+wx

%clean
rm -rf %{buildroot}

%files

%package %{modules_package}
Summary: %{vendor_name} %{driver_name} device drivers
Group: System Environment/Kernel
BuildRequires: gcc
BuildRequires: kernel-devel
BuildRequires: bc
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description %{modules_package}
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%post %{modules_package}
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun %{modules_package}
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans %{modules_package}
%{regenerate_initrd_posttrans}

%files %{modules_package}
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
/lib/modules/%{kernel_version}/%{module_dir}/*.ko
%exclude /etc/depmod.d/bnx2x.conf
%exclude %{_mandir}/man4/*

%changelog
* Mon Oct 22 2018 Rushikesh Jadhav <rushikesh7@gmail.com> - 7.14.46.1-1
- Updated the driver to latest version 7.14.46.1 and changed its name to qlogic-netxtreme2-alt
- Changed module_dir to updates/xcp-ng/%{driver_name}-%{version}
- The driver is now installed at a dedicated dir /lib/modules/%{kernel_version}/%{module_dir}
- Introduced Patch1000 to correct installation location in bnx2fc
- Removed Provides

* Mon Oct 23 2017 Simon Rowe <simon.rowe@citrix.com> - 7.14.29.1-1
- UPD-107: update netxtreme2 driver to 7.14.29.1 (QL-643)
