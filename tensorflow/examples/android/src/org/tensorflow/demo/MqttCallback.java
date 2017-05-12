package org.tensorflow.demo;

/**
 * Created by asad on 5/12/17.
 */

public interface MqttCallback {
    public void messageReceived(String message);
}
