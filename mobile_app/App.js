import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, SafeAreaView, StatusBar, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function App() {
  const [url, setUrl] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load saved URL on startup
    AsyncStorage.getItem('buniyaad_url').then((savedUrl) => {
      if (savedUrl) {
        setUrl(savedUrl);
        setInputUrl(savedUrl);
      }
      setLoading(false);
    });
  }, []);

  const handleConnect = async () => {
    let finalUrl = inputUrl.trim();
    if (!finalUrl.startsWith('http')) {
      finalUrl = 'http://' + finalUrl;
    }
    await AsyncStorage.setItem('buniyaad_url', finalUrl);
    setUrl(finalUrl);
  };

  const handleReset = async () => {
    await AsyncStorage.removeItem('buniyaad_url');
    setUrl('');
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#FFD600" />
      </View>
    );
  }

  if (!url) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#0D0F1A" />
        <View style={styles.setupCard}>
          <Text style={styles.title}>🎓 Buniyaad Admin</Text>
          <Text style={styles.subtitle}>Connect to your server to continue</Text>
          
          <Text style={styles.label}>Server IP / Localhost URL:</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 192.168.1.5:3000"
            placeholderTextColor="#8B92B0"
            value={inputUrl}
            onChangeText={setInputUrl}
            autoCapitalize="none"
            keyboardType="url"
          />
          
          <TouchableOpacity style={styles.btnPrimary} onPress={handleConnect}>
            <Text style={styles.btnText}>Connect</Text>
          </TouchableOpacity>

          <Text style={styles.hint}>
            Make sure your frontend and backend servers are running. Use your computer's local IP address if testing on a phone.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.webviewContainer}>
      <StatusBar barStyle="light-content" backgroundColor="#0D0F1A" />
      <WebView 
        source={{ uri: url }} 
        style={styles.webview}
        startInLoadingState={true}
        renderLoading={() => (
          <ActivityIndicator 
            style={styles.webviewLoader} 
            size="large" 
            color="#FFD600" 
          />
        )}
        onError={(syntheticEvent) => {
          const { nativeEvent } = syntheticEvent;
          console.warn('WebView error: ', nativeEvent);
          // If it fails to load, maybe the IP is wrong
        }}
      />
      <TouchableOpacity style={styles.floatingBtn} onPress={handleReset}>
        <Text style={styles.floatingBtnText}>⚙️</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D0F1A',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  setupCard: {
    backgroundColor: '#141626',
    padding: 30,
    borderRadius: 16,
    width: '100%',
    maxWidth: 400,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFD600',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#8B92B0',
    marginBottom: 32,
    textAlign: 'center',
  },
  label: {
    fontSize: 12,
    fontWeight: '600',
    color: '#8B92B0',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    borderRadius: 10,
    padding: 14,
    color: '#E8EAED',
    fontSize: 16,
    marginBottom: 20,
  },
  btnPrimary: {
    backgroundColor: '#1A237E',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
  },
  btnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  hint: {
    marginTop: 20,
    fontSize: 12,
    color: '#8B92B0',
    textAlign: 'center',
    lineHeight: 18,
  },
  webviewContainer: {
    flex: 1,
    backgroundColor: '#0D0F1A',
  },
  webview: {
    flex: 1,
    backgroundColor: '#0D0F1A',
  },
  webviewLoader: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginLeft: -18,
    marginTop: -18,
  },
  floatingBtn: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: '#1C1F35',
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  floatingBtnText: {
    fontSize: 24,
  }
});
