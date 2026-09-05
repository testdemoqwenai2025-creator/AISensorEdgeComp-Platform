name := "aisensoredgecomp-stream"
version := "0.1.0"
scalaVersion := "2.12.18"

libraryDependencies ++= Seq(
  "org.apache.flink" %% "flink-streaming-scala" % "1.19.0" % Provided,
  "org.apache.flink" %% "flink-connector-kafka" % "1.19.0" % Provided,
  "org.apache.flink" % "flink-avro" % "1.19.0",
  "org.apache.flink" %% "flink-statebackend-rocksdb" % "1.19.0" % Provided,
  "io.confluent" % "kafka-avro-serializer" % "7.6.0",
  "org.typelevel" %% "cats-core" % "2.12.0",
  "org.slf4j" % "slf4j-api" % "2.0.13",
)

assembly / assemblyMergeStrategy := {
  case PathList("META-INF", "MANIFEST.MF") => MergeStrategy.discard
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case _ => MergeStrategy.first
}
