import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.privatechat.app',
  appName: 'Private Chat',
  webDir: 'www' , 
  server: {
    url: 'http://10.0.2.2:8000',  // Android emulator
    cleartext: true
  },
  plugins: {
    BiometricAuth: {
      biometryTitle: "Biometric Authentication",
      biometrySubTitle: "Log in using biometric authentication",
      allowDeviceCredential: true
    }
  }
};

export default config;