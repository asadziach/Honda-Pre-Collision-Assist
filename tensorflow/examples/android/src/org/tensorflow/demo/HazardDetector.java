package org.tensorflow.demo;

import android.graphics.RectF;

import org.tensorflow.TensorFlow;


/**
 * Created by asad on 5/12/17.
 */


public class HazardDetector {

    private static final long WALABOT_DETECTION_EXPIRY = 500;
    private static final long ALERT_THRESHOLD = 1000;

    //This comes from maxInCm argument of wlbt.SetArenaR() call
    private static int ARENA_MAX = 100;
    /* Walabot arean covers the camera capture are from side to side.instead it only covers a
     * centre strip. This Walabot arena is mapped to TF detection arena by trail and error.
     */

    private static final int WALABOT_ARENA_START = 360;
    private static final int WALABOT_ARENA_MID = 720;
    private static final int WALABOT_ARENA_END = 1080;

    private static volatile int walabotReading;
    private static volatile long lastMessageTime;
    private static long lastAlertTime;

    private static MqttPublish mMqttPublish;

    public static void walabotDetection(Float reading){
        walabotReading = Math.round(reading);
        lastMessageTime = System.currentTimeMillis();
    }

    public static boolean isHazard(float recognition, float maxLength){

        boolean alertRaised = false;

        long currentTime = System.currentTimeMillis();

        if((currentTime - lastMessageTime) > WALABOT_DETECTION_EXPIRY){
            //Walabot has not detected anything recently.
            return false;
        }
        if(recognition > WALABOT_ARENA_START && recognition < WALABOT_ARENA_MID){
            /* TensorFlow has tracked a pedestrian to positive y of Walabot arena.
            * Check if Walabot affirms TensorFlow detection. */
            if(walabotReading > 0){
                alertRaised = true;
            }

        }

        if(!alertRaised && recognition > WALABOT_ARENA_MID && recognition < WALABOT_ARENA_END){
            /* TensorFlow has tracked a pedestrian to negative y of Walabot arena.
            * Check if Walabot affirms TensorFlow detection. */
            if(walabotReading < 0){
                alertRaised = true;
            }

        }

        if(alertRaised && (currentTime - lastAlertTime) > ALERT_THRESHOLD ){
            lastAlertTime = currentTime;
            if(mMqttPublish!=null){
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        mMqttPublish.messagePublish("ALERT");
                    }
                }).start();
            }
        }
        return alertRaised;
    }

    public static void registerPublisher(MqttPublish publisher) {
        mMqttPublish = publisher;
    }
}
