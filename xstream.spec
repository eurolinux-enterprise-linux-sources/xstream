# Copyright statement from JPackage this file is derived from:

# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Tests are disabled by default since we don't have
# all the requirements in Fedora yet
%bcond_with test

Name:           xstream
Version:        1.3.1
Release:        10%{?dist}
Summary:        Java XML serialization library

Group:          Development/Libraries
License:        BSD
URL:            http://xstream.codehaus.org/
Source0:        http://repository.codehaus.org/com/thoughtworks/%{name}/%{name}-distribution/%{version}/%{name}-distribution-%{version}-src.zip

# Backported from upstream revision 2210
Patch0:         %{name}-CVE-2013-7285.patch

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  jpackage-utils >= 0:1.7.2
BuildRequires:  ant >= 0:1.6
BuildRequires:  bea-stax >= 0:1.2.0
BuildRequires:  bea-stax-api >= 0:1.0.1
BuildRequires:  cglib >= 0:2.1.3
BuildRequires:  dom4j >= 0:1.6.1
BuildRequires:  jakarta-commons-lang >= 0:2.1
BuildRequires:  jakarta-oro
BuildRequires:  jdom >= 0:1.0
BuildRequires:  jettison >= 0:1.0
BuildRequires:  joda-time >= 0:1.2.1
BuildRequires:  junit >= 0:3.8.1
BuildRequires:  xpp3 >= 0:1.1.3.4
BuildRequires:  unzip
BuildRequires:  java-devel-openjdk
%if %with test
BuildRequires:  jmock >= 0:1.0.1
BuildRequires:  wstx >= 0:3.2.0
%endif
Requires:       jpackage-utils
Requires:       java
Requires:       xpp3-minimal

BuildArch:      noarch


%description
XStream is a simple library to serialize objects to XML 
and back again. A high level facade is supplied that 
simplifies common use cases. Custom objects can be serialized 
without need for specifying mappings. Speed and low memory 
footprint are a crucial part of the design, making it suitable 
for large object graphs or systems with high message throughput. 
No information is duplicated that can be obtained via reflection. 
This results in XML that is easier to read for humans and more 
compact than native Java serialization. XStream serializes internal 
fields, including private and final. Supports non-public and inner 
classes. Classes are not required to have default constructor. 
Duplicate references encountered in the object-model will be 
maintained. Supports circular references. By implementing an 
interface, XStream can serialize directly to/from any tree 
structure (not just XML). Strategies can be registered allowing 
customization of how particular types are represented as XML. 
When an exception occurs due to malformed XML, detailed diagnostics 
are provided to help isolate and fix the problem.


%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description    javadoc
%{name} API documentation.


%prep
%setup -qn %{name}-%{version}
%patch0 -p1
find . -name "*.jar" -delete

%if %with test
# This test requires megginson's sax2
rm -f xstream/src/test/com/thoughtworks/xstream/io/xml/SaxWriterTest.java
%endif

find -name XomDriver.java -delete
find -name XomReader.java -delete
find -name XomWriter.java -delete


%build
# Replace bundled tars
pushd xstream/lib
ln -sf $(build-classpath cglib)
ln -sf $(build-classpath commons-lang)
ln -sf $(build-classpath dom4j)
ln -sf $(build-classpath jdom)
ln -sf $(build-classpath jettison)
ln -sf $(build-classpath joda-time)
ln -sf $(build-classpath junit)
ln -sf $(build-classpath oro)
ln -sf $(build-classpath bea-stax-ri)
ln -sf $(build-classpath bea-stax-api)
ln -sf $(build-classpath xpp3)
%if %with test
ln -sf $(build-classpath jmock)
ln -sf $(build-classpath wstx/wstx-asl)
%endif
popd

# Build
pushd xstream
%if %with test
ant library javadoc
%else
ant benchmark:compile jar javadoc
%endif
popd


%install
rm -rf $RPM_BUILD_ROOT

# Directory structure
install -d $RPM_BUILD_ROOT%{_javadir}
install -d $RPM_BUILD_ROOT%{_javadocdir}

# Main jar
pushd xstream
install -p -m644 target/xstream-SNAPSHOT.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# Benchmarks
install -p -m644 target/xstream-benchmark-SNAPSHOT.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{name}-benchmark.jar

# API Documentation
cp -pr target/javadoc $RPM_BUILD_ROOT%{_javadocdir}/%{name}
popd

# POMs
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{name}-parent.pom
%add_maven_depmap JPP-%{name}-parent.pom

install -pm 644 xstream/pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap


%files
%{_javadir}/*.jar
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*
%doc LICENSE.txt


%files javadoc
%{_javadocdir}/%{name}
%doc LICENSE.txt


%changelog
* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-10
- Apply upstream security patch
- Resolves: CVE-2013-7285

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.3.1-9
- Mass rebuild 2013-12-27

* Wed Sep 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-8
- Disable support for XOM

* Fri Jul 12 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-7
- Update to current packaging guidelines

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-6
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jun 14 2010 Alexander Kurtakov <akurtako@redhat.com> 1.3.1-1
- Update to 1.3.1.
- Install maven pom and depmap.

* Wed Dec 02 2009 Lubomir Rintel <lkundrak@v3.sk> - 1.2.2-4
- Cosmetic fixes

* Fri Nov 27 2009 Lubomir Rintel <lkundrak@v3.sk> - 0:1.2.2-3
- Drop gcj (suggested by Jochen Schmitt), we seem to need OpenJDK anyway
- Fix -javadoc Require
- Drop epoch

* Sun Nov 01 2009 Lubomir Rintel <lkundrak@v3.sk> - 0:1.2.2-2
- Greatly simplify for Fedora
- Disable tests, we don't have all that's required to run them
- Remove maven build

* Fri Jul 20 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.2.2-1jpp
- Upgrade to 1.2.2
- Build with maven2 by default
- Add poms and depmap frags

* Tue May 23 2006 Ralph Apel <r.apel at r-apel.de> - 0:1.1.3-1jpp
- Upgrade to 1.1.3
- Patched to work with bea

* Mon Sep 13 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.2-2jpp
- Drop saxpath requirement
- Require jaxen >= 0:1.1

* Mon Aug 30 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.2-1jpp
- Upgrade to 1.0.2
- Delete included binary jars
- Change -Dbuild.sysclasspath "from only" to "first" (DynamicProxyTest)
- Relax some versioned dependencies
- Build with ant-1.6.2

* Fri Aug 06 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.1-2jpp
- Upgrade to ant-1.6.X

* Tue Jun 01 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0.1-1jpp
- Upgrade to 1.0.1

* Fri Feb 13 2004 Ralph Apel <r.apel at r-apel.de> - 0:0.3-1jpp
- Upgrade to 0.3
- Add manual subpackage

* Mon Jan 19 2004 Ralph Apel <r.apel at r-apel.de> - 0:0.2-1jpp
- First JPackage release
