FROM openjdk:8-alpine

# install software:
# curl for download
# procps to replace 'ps' from busybox, required by ODL scripts
# tini as init in container
RUN apk add --no-cache curl procps tini && \
	curl -L https://nexus.opendaylight.org/content/repositories/public/org/opendaylight/integration/karaf/0.8.4/karaf-0.8.4.tar.gz -o /odl.tar.gz && \
	tar -xzf /odl.tar.gz && \
	rm /odl.tar.gz

# install karaf features
ARG ODL_FEATURES=odl-l2switch-switch,odl-restconf,odl-restconf-all,odl-netconf-connector-all,odl-netconf-mdsal

WORKDIR /karaf-0.8.4
RUN sed -i "/^featuresBoot =/ s/$/,${ODL_FEATURES}/" etc/org.apache.karaf.features.cfg

# specify entrypoint
COPY entrypoint.sh /karaf-0.8.4/bin/entrypoint.sh
ENTRYPOINT [ "/sbin/tini", "--" ]
CMD [ "bin/entrypoint.sh" ]
