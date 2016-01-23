# remirepo/fedora spec file for php-league-flysystem
#
# Copyright (c) 2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
# Github
%global gh_commit    183e1a610664baf6dcd6fceda415baf43cbdc031
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     thephpleague
%global gh_project   flysystem
# Packagist
%global pk_vendor    league
%global pk_name      flysystem
# PSR-0 namespace
%global ns_vendor    League
%global ns_project   Flysystem

Name:           php-%{pk_vendor}-%{pk_name}
Version:        1.0.16
Release:        1%{?dist}
Summary:        Filesystem abstraction: Many filesystems, one API

Group:          Development/Libraries
License:        MIT
URL:            https://github.com/%{gh_owner}/%{gh_project}
Source0:        %{name}-%{version}-%{gh_short}.tgz
# Create git snapshot as tests are excluded from official tarball
Source1:        makesrc.sh
# Autoloader
Source2:        %{name}-autoload.php

# https://github.com/thephpleague/flysystem/pull/592
Patch1:         %{name}-pr592.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php(language) >= 5.4
BuildRequires:  php-date
BuildRequires:  php-fileinfo
BuildRequires:  php-ftp
BuildRequires:  php-mbstring
BuildRequires:  php-pcre
BuildRequires:  php-spl
# From composer.json, "require-dev": {
#        "phpunit/phpunit": "~4.8", => 5.x is ok
#        "mockery/mockery": "~0.9",
#        "phpspec/phpspec": "^2.2",
#        "phpspec/prophecy-phpunit": "~1.0" => unneeded see our patch
BuildRequires:  php-composer(phpunit/phpunit) >= 4.0
BuildRequires:  php-composer(mockery/mockery) >= 0.9
BuildRequires:  php-composer(phpspec/phpspec) >= 2.2
# Autoloader
BuildRequires:  php-composer(symfony/class-loader)

# From composer.json, "require": {
#        "php": ">=5.4.0"
Requires:       php(language) >= 5.4
# From phpcompatifo report for 1.0.16
Requires:       php-date
Requires:       php-fileinfo
Requires:       php-ftp
Requires:       php-mbstring
Requires:       php-pcre
Requires:       php-spl
# Autoloader
Requires:       php-composer(symfony/class-loader)

Provides:       php-composer(%{pk_vendor}/%{pk_name}) = %{version}


%description
Flysystem is a filesystem abstraction which allows you to easily swap out
a local filesystem for a remote one.

Autoloader: %{_datadir}/php/%{ns_vendor}/%{ns_project}/autoload.php


%prep
%setup -q -n %{gh_project}-%{gh_commit}

%patch1 -p1
install -pm 644 %{SOURCE2} src/autoload.php


%build
# Nothing


%install
rm -rf     %{buildroot}

# Restore PSR-0 tree
mkdir -p   %{buildroot}%{_datadir}/php/%{ns_vendor}
cp -pr src %{buildroot}%{_datadir}/php/%{ns_vendor}/%{ns_project}


%check
: Generate a simple autoloader
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
// Installed library
require '%{buildroot}%{_datadir}/php/%{ns_vendor}/%{ns_project}/autoload.php';

// Dependency
require_once '%{_datadir}/php/Mockery/autoload.php';

// Test suite
require_once '%{_datadir}/php/Symfony/Component/ClassLoader/Psr4ClassLoader.php';
$Loader = new \Symfony\Component\ClassLoader\Psr4ClassLoader();
$Loader->addPrefix("League\\Flysystem\\Stub\\", dirname(__DIR__).'/stub');
$Loader->register();
EOF

: Fix bootstraping
sed -e 's/file="[^"]*"//' -i phpunit.xml
echo 'bootstrap: vendor/autoload.php' >>phpspec.yml

: Run upstream test suite
%{_bindir}/phpspec run
%{_bindir}/phpunit --verbose

if which php70; then
  : Run upstream test suite with PHP 7
  php70 %{_bindir}/phpspec run
  php70 %{_bindir}/phpunit --verbose
fi

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md
%doc composer.json
%{_datadir}/php/%{ns_vendor}


%changelog
* Thu Jan 14 2016 Remi Collet <remi@fedoraproject.org> - 1.0.16-1
- initial package
- open https://github.com/thephpleague/flysystem/pull/592 - PHPUnit