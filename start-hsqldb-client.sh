mvn dependency:copy-dependencies -DincludeArtifactIds=hsqldb
cp target/dependency/hsqldb*.jar data/
java -jar data/hsqldb*.jar

