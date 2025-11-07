import { useState, useEffect } from 'react';
import '@/App.css';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Copy, Mail, Lock, CheckCircle, Clock, RefreshCw } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [loading, setLoading] = useState(false);
  const [currentAccount, setCurrentAccount] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoadingAccounts(true);
    try {
      const response = await axios.get(`${API}/accounts`);
      setAccounts(response.data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      toast.error('Gagal memuat daftar akun');
    } finally {
      setLoadingAccounts(false);
    }
  };

  const generateAccount = async () => {
    setLoading(true);
    setCurrentAccount(null);
    
    try {
      const response = await axios.post(`${API}/generate`);
      setCurrentAccount(response.data);
      toast.success('Akun berhasil dibuat!');
      
      // Refresh account list
      await fetchAccounts();
    } catch (error) {
      console.error('Error generating account:', error);
      const errorMsg = error.response?.data?.detail || 'Gagal membuat akun';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} berhasil disalin!`);
  };

  return (
    <div className="App">
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-4">
              Emergent Account Generator
            </h1>
            <p className="text-lg text-slate-600">Generate akun Emergent.sh secara otomatis</p>
          </div>

          {/* Generate Section */}
          <Card className="mb-8 border-2 border-indigo-100 shadow-xl" data-testid="generate-card">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-2xl text-slate-900">Generate Akun Baru</CardTitle>
              <CardDescription>Klik tombol di bawah untuk membuat akun baru</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-6 pb-8">
              <Button
                onClick={generateAccount}
                disabled={loading}
                size="lg"
                className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white px-8 py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                data-testid="generate-btn"
              >
                {loading ? (
                  <>
                    <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                    Membuat akun...
                  </>
                ) : (
                  '🎯 Generate Akun'
                )}
              </Button>

              {loading && (
                <div className="text-center" data-testid="loading-indicator">
                  <p className="text-slate-600 mb-2">Sedang membuat akun...</p>
                  <p className="text-sm text-slate-500">Proses ini membutuhkan 30-60 detik</p>
                </div>
              )}

              {currentAccount && !loading && (
                <div className="w-full max-w-2xl mt-4" data-testid="current-account">
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 shadow-lg">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                      <h3 className="text-xl font-bold text-green-800">Akun Berhasil Dibuat!</h3>
                    </div>

                    <div className="space-y-4">
                      <div className="bg-white rounded-lg p-4 border border-green-200">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3 flex-1">
                            <Mail className="h-5 w-5 text-indigo-600" />
                            <div className="flex-1">
                              <p className="text-xs text-slate-500 mb-1">Email</p>
                              <p className="font-mono text-sm text-slate-900 break-all" data-testid="account-email">
                                {currentAccount.email}
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(currentAccount.email, 'Email')}
                            className="ml-2 hover:bg-indigo-100"
                            data-testid="copy-email-btn"
                          >
                            <Copy className="h-4 w-4 text-indigo-600" />
                          </Button>
                        </div>
                      </div>

                      <div className="bg-white rounded-lg p-4 border border-green-200">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3 flex-1">
                            <Lock className="h-5 w-5 text-indigo-600" />
                            <div className="flex-1">
                              <p className="text-xs text-slate-500 mb-1">Password</p>
                              <p className="font-mono text-sm text-slate-900" data-testid="account-password">
                                {currentAccount.password}
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(currentAccount.password, 'Password')}
                            className="ml-2 hover:bg-indigo-100"
                            data-testid="copy-password-btn"
                          >
                            <Copy className="h-4 w-4 text-indigo-600" />
                          </Button>
                        </div>
                      </div>

                      {currentAccount.verified && (
                        <div className="flex items-center gap-2 text-green-700 bg-green-100 rounded-lg p-3">
                          <CheckCircle className="h-5 w-5" />
                          <span className="text-sm font-medium">Akun sudah diverifikasi</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Accounts List */}
          <Card className="border-2 border-slate-200 shadow-xl" data-testid="accounts-list-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl text-slate-900">Daftar Akun</CardTitle>
                  <CardDescription>Total: {accounts.length} akun</CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchAccounts}
                  disabled={loadingAccounts}
                  className="border-indigo-200 hover:bg-indigo-50"
                  data-testid="refresh-accounts-btn"
                >
                  <RefreshCw className={`h-4 w-4 ${loadingAccounts ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loadingAccounts ? (
                <div className="text-center py-8" data-testid="accounts-loading">
                  <RefreshCw className="h-8 w-8 animate-spin mx-auto text-indigo-600 mb-2" />
                  <p className="text-slate-600">Memuat akun...</p>
                </div>
              ) : accounts.length === 0 ? (
                <div className="text-center py-12" data-testid="no-accounts">
                  <Clock className="h-12 w-12 mx-auto text-slate-300 mb-3" />
                  <p className="text-slate-500">Belum ada akun yang dibuat</p>
                  <p className="text-sm text-slate-400 mt-1">Generate akun pertama Anda!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {accounts.slice().reverse().map((account, index) => (
                    <div
                      key={index}
                      className="bg-slate-50 border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      data-testid={`account-item-${index}`}
                    >
                      <div className="grid md:grid-cols-2 gap-3">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-slate-400 flex-shrink-0" />
                          <p className="font-mono text-xs text-slate-700 break-all flex-1">
                            {account.email}
                          </p>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(account.email, 'Email')}
                            className="h-8 w-8 p-0 hover:bg-slate-200"
                            data-testid={`copy-email-${index}`}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="flex items-center gap-2">
                          <Lock className="h-4 w-4 text-slate-400 flex-shrink-0" />
                          <p className="font-mono text-xs text-slate-700 flex-1">
                            {account.password}
                          </p>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(account.password, 'Password')}
                            className="h-8 w-8 p-0 hover:bg-slate-200"
                            data-testid={`copy-password-${index}`}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      {account.verified && (
                        <div className="flex items-center gap-1 mt-2">
                          <CheckCircle className="h-3 w-3 text-green-600" />
                          <span className="text-xs text-green-700">Verified</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-center mt-8 text-sm text-slate-500">
            <p>Powered by Emergent Account Generator</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
