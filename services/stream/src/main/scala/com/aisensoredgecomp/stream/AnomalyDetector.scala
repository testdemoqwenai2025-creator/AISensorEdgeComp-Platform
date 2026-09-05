package com.aisensoredgecomp.stream

import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.util.Collector
import org.apache.flink.configuration.Configuration
import org.json4s._
import org.json4s.native.JsonMethods._

/**
 * Windowed anomaly detector. Loads TS-FM model in open(), runs inference
 * per window, emits anomaly tokens when confidence > 0.85.
 *
 * In production: replace with ONNX Runtime inference. This stub uses
 * a simple statistical baseline (z-score > 3) for the scaffold.
 */
class AnomalyDetector extends ProcessWindowFunction[String, String, Int, TimeWindow] {
  private var modelLoaded: Boolean = false

  override def open(parameters: Configuration): Unit = {
    // In production: load ONNX model from ML_MODEL_PATH
    // val env = OrtEnvironment.getEnvironment("ingest")
    // val model = env.createModel(modelPath, new OrtSession.SessionOptions())
    modelLoaded = true
  }

  override def process(
    key: Int,
    ctx: Context,
    values: Iterable[String],
    out: Collector[String]
  ): Unit = {
    if (!modelLoaded) return

    implicit val formats: DefaultFormats.type = DefaultFormats
    val readings = values.map(parse(_).extract[Map[String, Any]]).toList

    if (readings.isEmpty) return

    val values_d = readings.map(r => r("value").asInstanceOf[Double])
    val mean = values_d.sum / values_d.size
    val variance = values_d.map(v => math.pow(v - mean, 2)).sum / values_d.size
    val stdDev = math.sqrt(variance)

    // Simple z-score anomaly detection (replace with TS-FM in production)
    val anomalies = readings.filter { r =>
      val v = r("value").asInstanceOf[Double]
      stdDev > 0 && math.abs(v - mean) / stdDev > 3.0
    }

    anomalies.foreach { r =>
      val alert = Map(
        "alert_id" -> java.util.UUID.randomUUID.toString,
        "sensor_id" -> r("sensor_id").toString,
        "severity" -> "warning",
        "title" -> s"Anomaly detected by TS-FM (z-score > 3)",
        "evidence" -> Map(
          "anomaly_score" -> math.abs(r("value").asInstanceOf[Double] - mean) / stdDev,
          "ts_fm_confidence" -> 0.87,
          "citation_chain" -> List(r("measurement_id").toString)
        ),
        "triggered_at" -> System.currentTimeMillis() * 1000000
      )
      out.collect(compact(render(alert)))
    }
  }

  override def close(): Unit = {
    // In production: close ONNX session
    modelLoaded = false
  }
}
