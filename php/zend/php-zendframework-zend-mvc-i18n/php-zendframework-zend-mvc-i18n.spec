# remirepo/Fedora spec file for php-zendframework-zend-mvc-i18n
#
# Copyright (c) 2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global bootstrap    0
%global gh_commit    5a7068160d3884263932c919c2250cb4a4a66501
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     zendframework
%global gh_project   zend-mvc-i18n
%global php_home     %{_datadir}/php
%global library      I18n
%if %{bootstrap}
%global with_tests   0%{?_with_tests:1}
%else
%global with_tests   0%{!?_without_tests:1}
%endif

Name:           php-%{gh_owner}-%{gh_project}
Version:        1.0.0
Release:        1%{?dist}
Summary:        Zend Framework Mvc-%{library} component

Group:          Development/Libraries
License:        BSD
URL:            https://framework.zend.com/
Source0:        %{gh_commit}/%{name}-%{version}-%{gh_short}.tgz
Source1:        makesrc.sh

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:      noarch
# Tests
%if %{with_tests}
BuildRequires:  php(language) >= 5.6
BuildRequires:  php-composer(container-interop/container-interop) >= 1.1
BuildRequires:  php-composer(%{gh_owner}/zend-i18n)               >= 2.7
BuildRequires:  php-composer(%{gh_owner}/zend-router)             >= 3.0
BuildRequires:  php-composer(%{gh_owner}/zend-servicemanager)     >= 2.7.5
BuildRequires:  php-composer(%{gh_owner}/zend-stdlib)             >= 2.7.6
BuildRequires:  php-composer(%{gh_owner}/zend-validator)          >= 2.6
BuildRequires:  php-intl
BuildRequires:  php-spl
# From composer, "require-dev": {
#        "phpunit/phpunit": "^4.5",
#        "squizlabs/php_codesniffer": "^2.3.1",
#        "zendframework/zend-cache": "^2.6.1"
BuildRequires:  php-composer(phpunit/phpunit)                     >= 4.5
BuildRequires:  php-composer(%{gh_owner}/zend-cache)              >= 2.6.1
# Autoloader
BuildRequires:  php-composer(%{gh_owner}/zend-loader)           >= 2.5
# For dependencies autoloader
BuildRequires:  php-zendframework-zend-loader                   >= 2.5.1-3
%endif

# From composer, "require": {
#        "php": "^5.6 || ^7.0",
#        "container-interop/container-interop": "^1.1",
#        "zendframework/zend-i18n": "^2.7",
#        "zendframework/zend-router": "^3.0",
#        "zendframework/zend-servicemanager": "^2.7.5 || ^3.0.3",
#        "zendframework/zend-stdlib": "^2.7.6 || ^3.0",
#        "zendframework/zend-validator": "^2.6"
Requires:       php(language) >= 5.6
Requires:       php-composer(container-interop/container-interop) >= 1.1
Requires:       php-composer(container-interop/container-interop) <  2
Requires:       php-composer(%{gh_owner}/zend-i18n)               >= 2.7
Requires:       php-composer(%{gh_owner}/zend-i18n)               <  3
Requires:       php-composer(%{gh_owner}/zend-router)             >= 3.0
Requires:       php-composer(%{gh_owner}/zend-router)             <  4
Requires:       php-composer(%{gh_owner}/zend-servicemanager)     >= 2.7.5
Requires:       php-composer(%{gh_owner}/zend-servicemanager)     <  4
Requires:       php-composer(%{gh_owner}/zend-stdlib)             >= 2.7.6
Requires:       php-composer(%{gh_owner}/zend-stdlib)             <  4
Requires:       php-composer(%{gh_owner}/zend-validator)          >= 2.6
Requires:       php-composer(%{gh_owner}/zend-validator)          <  3
# From phpcompatinfo report for version 1.0.0
Requires:       php-intl
Requires:       php-spl
%if ! %{bootstrap}
# From composer, "suggest": {
#        "zendframework/zend-cache": "To enable caching of translation strings"
%if 0%{?fedora} >= 21
Suggests:       php-composer(%{gh_owner}/zend-cache)
%endif
# Autoloader
Requires:       php-composer(%{gh_owner}/zend-loader)           >= 2.5
Requires:       php-zendframework-zend-loader                   >= 2.5.1-3
%endif

Provides:       php-composer(%{gh_owner}/%{gh_project}) = %{version}


%description
zend-mvc-i18n provides integration between:

* zend-i18n
* zend-mvc
* zend-router

and replaces the i18n functionality found in the v2 releases of the latter
two components.

* File issues at https://github.com/zendframework/zend-mvc-i18n/issues
* Documentation is at https://zendframework.github.io/zend-mvc-i18n/


%prep
%setup -q -n %{gh_project}-%{gh_commit}

mv LICENSE.md LICENSE

: Create dependency autoloader
cat << 'EOF' | tee autoload.php
<?php
require_once '%{php_home}/Interop/Container/autoload.php';
EOF


%build
# Empty build section, nothing required


%install
rm -rf %{buildroot}

mkdir -p   %{buildroot}%{php_home}/Zend/Mvc
cp -pr src %{buildroot}%{php_home}/Zend/Mvc/%{library}

install -m644 autoload.php %{buildroot}%{php_home}/Zend/Mvc-%{library}-autoload.php


%check
%if %{with_tests}
mkdir vendor
cat << 'EOF' | tee vendor/autoload.php
<?php
define('RPM_BUILDROOT', '%{buildroot}%{php_home}/Zend');

require_once '%{php_home}/Zend/Loader/AutoloaderFactory.php';
Zend\Loader\AutoloaderFactory::factory(array(
    'Zend\Loader\StandardAutoloader' => array(
        'namespaces' => array(
           'ZendTest\\Mvc\\%{library}' => dirname(__DIR__).'/test/',
           'Zend\\Mvc\\%{library}'     => '%{buildroot}%{php_home}/Zend/Mvc/%{library}'
))));
require_once '%{php_home}/Zend/autoload.php';
EOF

# remirepo:11
run=0
ret=0
if which php56; then
   php56 %{_bindir}/phpunit --include-path=%{buildroot}%{php_home} || ret=1
   run=1
fi
if which php71; then
   php70 %{_bindir}/phpunit --include-path=%{buildroot}%{php_home} || ret=1
   run=1
fi
if [ $run -eq 0 ]; then
%{_bindir}/phpunit --include-path=%{buildroot}%{php_home} --verbose
# remirepo:2
fi
exit $ret
%else
: Test suite disabled
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md
%doc composer.json
%{php_home}/Zend/Mvc/%{library}
%{php_home}/Zend/Mvc-%{library}-autoload.php


%changelog
* Wed Jun 29 2016 Remi Collet <remi@fedoraproject.org> - 1.1.10-1
- initial package

