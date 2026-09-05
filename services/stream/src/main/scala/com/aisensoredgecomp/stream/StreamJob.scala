package com.aisensoredgecomp.stream

import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.connectors.kafka.{FlinkKafkaConsumer, FlinkKafkaProducer}
import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.api.java.utils.ParameterTool
import java.util.Properties

/**
 * Main streaming job: consume telemetry from Kafka, run TS-FM anomaly
 * detection, emit anomaly tokens to alerts topic, archive to Iceberg.
 */
object StreamJob {
  def main(args: Array[String]): Unit = {
    val params = ParameterTool.fromArgs(args)
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    env.enableCheckpointing(60000)  // 60s
    env.setStateBackend(new org.apache.flink.contrib.streaming.state.RocksDBStateBackendFactory().create())

    val kafkaProps = new Properties()
    kafkaProps.setProperty("bootstrap.servers", params.getRequired("bootstrap.servers"))
    kafkaProps.setProperty("group.id", "aisensoredgecomp-stream")

    // Source: raw telemetry
    val telemetry: DataStream[String] = env.addSource(
      new FlinkKafkaConsumer[String](
        "telemetry.raw",
        new SimpleStringSchema(),
        kafkaProps
      )
    ).name("telemetry-source")

    // Window: 30-second tumbling windows per sensor
    val anomalies = telemetry
      .keyBy(_.hashCode)  // In production: key by sensor_id parsed from JSON
      .timeWindow(Time.seconds(30))
      .process(new AnomalyDetector)
      .name("anomaly-detector")

    // Sink 1: alerts topic
    anomalies.addSink(
      new FlinkKafkaProducer[String](
        params.getRequired("bootstrap.servers"),
        "alerts.processed",
        new SimpleStringSchema()
      )
    ).name("alerts-sink")

    // Sink 2: archive to Iceberg (via IcebergSink — see flink-iceberg connector)
    // anomalies.addSink(IcebergSink.forStreamer(...).build())

    env.execute("AISensorEdgeComp Stream Job")
  }
}
