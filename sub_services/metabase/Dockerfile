FROM metabase/metabase:v0.51.1.2

# Download the ClickHouse plugin and place it in the plugins directory
ADD https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.51.0/clickhouse.metabase-driver.jar /plugins/


# Set the entrypoint to the Metabase jar file
ENTRYPOINT ["java", "-jar", "/app/metabase.jar"]

# Set default command
CMD []
