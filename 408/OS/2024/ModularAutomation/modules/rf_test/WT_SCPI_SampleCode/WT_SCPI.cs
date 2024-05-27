using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace WT_SCPI_SampleCode
{
    public enum SignalDemod
    {
        Demod11ag,
        Demod11b,
        Demod11n20,
        Demod11n40,
        Demod11ac20,
        Demod11ac40,
        Demod11ac80,
        Demod11ac160,
        Demod11ac8080,
        DemodBluetooth,
        DemodZigbee,
        DemodCW = 16,
        Demod11ax20 = 22,
        Demod11ax40,
        Demod11ax80,
        Demod11ax160,
        Demod11ax8080,
        Demod11be20 = 34,
        Demod11be40,
        Demod11be80,
        Demod11be160,
        Demod11be8080,
    }

    public class WT_SCPI
    {
        TcpClient tcpClient = new TcpClient();

        public void Connect(string ip)
        {
            IPAddress ipaddr = IPAddress.Parse(ip);
            tcpClient = new TcpClient();
            tcpClient.Connect(ipaddr, 5025);
            Write("WT:SYSTem:CMD:RESPonse 0\n");
        }

        public void Disconnect()
        {
            tcpClient?.Close();
        }

        public void Write(string cmd)
        {
            var netStream = tcpClient.GetStream();
            byte[] byteData = Encoding.ASCII.GetBytes(cmd);
            netStream.Write(byteData, 0, byteData.Length);
        }
        
        public void Write(byte[] cmd)
        {
            var netStream = tcpClient.GetStream();
            netStream.Write(cmd, 0, cmd.Length);
        }

        public string Read()
        {
            string content = string.Empty;
            var netStream = tcpClient.GetStream();
            if (netStream.CanRead && netStream.DataAvailable)
            {
                int recvCnt = tcpClient.Available;
                if (recvCnt > 0)
                {
                    var recvBuf = new byte[recvCnt];
                    netStream.Read(recvBuf, 0, recvCnt);
                    var showResponse = Encoding.ASCII.GetString(recvBuf, 0, recvCnt);
                    content = showResponse;
                }
            }
            return content;
        }

        public void ClearBuf()
        {
            var netStream = tcpClient.GetStream();
            while (netStream.CanRead && netStream.DataAvailable)
            {
                var recvCnt = tcpClient.Available;
                if (recvCnt > 0)
                {
                    var recvBuf = new byte[recvCnt];
                    netStream.Read(recvBuf, 0, recvCnt);
                    var showResponse = Encoding.ASCII.GetString(recvBuf, 0, recvCnt);
                }
            }
        }

        public string Query(string cmd, string ack = "\n", int timeout = 3000)
        {
            Write(cmd);

            var total = string.Empty;
            Stopwatch sw = new Stopwatch();
            sw.Start();
            while (sw.ElapsedMilliseconds < timeout)
            {
                var response = Read();
                if (response.Length > 0)
                {
                    total += response;
                    if (total.Contains(ack))
                    {
                        break;
                    }
                }
            }
            sw.Stop();
            return total;
        }

        public void CheckError(string content, int timeout = 3000)
        {
            var err = Query("SYST:ERR?\n", "\n", timeout);
            if (!err.Contains("\"No error\"\r\n"))
            {
                throw new Exception($"{content} Check Error: {err}");
            }
        }

        public void UploadWaveForm(string fileName)
        {
            var waveName = Path.GetFileName(fileName);
            var waveInfo = File.ReadAllBytes(fileName);
            var waveSize = waveInfo.Length.ToString();
            var cmd = $"WT:SOURce:CONFigure:SAVE:WAVE \"{waveName}\",0,#{waveSize.Length}{waveSize}";
            Write(cmd);
            Write(waveInfo);
            Write("\n");
            CheckError("UploadWaveForm");
        }

        private void WaitForVsgComplete(int timeout=5000)
        {
            Stopwatch sw = new Stopwatch();
            sw.Start();
            while (sw.ElapsedMilliseconds < timeout)
            {
                var state = Query("WT:SOURce:CURRent:STATe?\n").Trim();
                if (state == "0")    // done
                    return;
                else if (state == "1")  // running
                    continue;
                else if (state == "4")  // waiting
                    continue;
                else if (state == "2")  // timeout
                    throw new Exception("vsg state timeout");
                else
                    throw new Exception("vsg state error: " + state);
            }
            sw.Stop();
            throw new Exception("vsg state timeout");
        }

        private void WaitForVsgStart(int timeout = 5000)
        {
            Stopwatch sw = new Stopwatch();
            sw.Start();
            while (sw.ElapsedMilliseconds < timeout)
            {
                var state = Query("WT:SOURce:CURRent:STATe?\n").Trim();
                if (state == "0")    // done
                    throw new Exception("vsg done");
                else if (state == "1")  // running
                    return;
                else if (state == "4")  // waiting
                    continue;
                else if (state == "2")  // timeout
                    throw new Exception("vsg state timeout");
                else
                    throw new Exception("vsg state error: " + state);
            }
            sw.Stop();
            throw new Exception("vsg state timeout");
        }

        public void Vsg(int port, int freqMHz, int sampleRateMHz, int packets, string wave)
        {
            List<string> cmds = new List<string>
            {
                $"WT:SOURce:CONFigure:REPEat {packets}",
                "WT:SOURce:CONFigure:WAVE:GAP 5e-5",
                $"WT:SOURce:CONFigure:WAVE '{wave}'",
                $"WT:SOURce:CONFigure:FREQuency {freqMHz}e+06",
                $"WT:SOURce:CONFigure:SAMPle:RATE {sampleRateMHz}e+06",
                "WT:SOURce:CONFigure:POWer -10",
                $"WT:SOURce:CONFigure:RFPOrt {port + 1}",
                "WT:SOURce:CONFigure:TMOWaitting 8",
                "WT:SOURce:CONFigure:FREQuency:OFFSet 0",
                "WT:SOURce:CONFigure:EXT1:GAIN 0",
                "WT:SOURce:STARt"
            };
            string cmd = string.Join("\n", cmds) + "\n";
            // Console.Write(cmd);
            Write(cmd);
            CheckError("VSG");

            if (packets == 0)
            {
                WaitForVsgStart();
            }
            else
            {
                WaitForVsgComplete();
            }
        }

        public void StopVsg()
        {
            Write("WT:SOURce:STOP\n");
        }

        public void Vsa(int port, int freqMHz, int sampleRateMHz, SignalDemod demod, bool agc = true, double targetPower = 0.0)
        {
            var cmds = new List<string>
            {
                "WT:SENSe:STOP:CAPTure",
                "WT:SENSe:CONFigure:TRIGer:TYPE 2",
                $"WT:SENSe:CONFigure:FREQuency {freqMHz}e+06",
                "WT:SENSe:CONFigure:FREQuency:OFFSet 0",
                $"WT:SENSe:CONFigure:MAXPower {targetPower + 12.0}",
                "WT:SENSe:CONFigure:TRIGer:LEVEl -31",
                $"WT:SENSe:CONFigure:RFPOrt {port + 1}",
                $"WT:SENSe:CONFigure:DEMOd {(int)demod}",
                "WT:SENSe:CONFigure:MAX:IFG 0.2",
                "WT:SENSe:CONFigure:TRIGer:TMO 1",
                "WT:WIFI:SENSe:CONFigure:TRIGer:PRETime 2E-05",
                "WT:SENSe:CONFigure:SMPTime 500e-6",
                $"WT:SENSe:CONFigure:SAMPle:RATE {sampleRateMHz}e6",
                "WT:SENSe:CONFigure:TMOWaitting 8",
                "WT:SENSe:CONFigure:EXT1:GAIN 0",

                // analyze parameter
                "WT:WIFI:SENSe:CONFigure:ANALy:BANDwidth:MODE 0",
                $"WT:WIFI:SENSe:CONFigure:ANALy:DEMOd {(int)demod}",
                "WT:WIFI:SENSe:CONFigure:ANALy:DSSS:DC:REMOval 0",
                "WT:WIFI:SENSe:CONFigure:ANALy:DSSS:EVM:METHod 1",
                "WT:WIFI:SENSe:CONFigure:ANALy:DSSS:PH:CORR 2",
                "WT:WIFI:SENSe:CONFigure:ANALy:DSSS:EQ:TAPS 1",
                "WT:WIFI:SENSe:CONFigure:ANALy:OFDM:PH:CORR 2",
                "WT:WIFI:SENSe:CONFigure:ANALy:OFDM:CH:ESTImate 1",
                "WT:WIFI:SENSe:CONFigure:ANALy:OFDM:SYM:TIME:CORR 2",
                "WT:WIFI:SENSe:CONFigure:ANALy:OFDM:FREQ:SYNC 2",
                "WT:WIFI:SENSe:CONFigure:ANALy:OFDM:AMPL:TRACk 1",
                "WT:WIFI:SENSe:CONFigure:ANALy:CLOCk:RATE 1",
                "WT:SENSe:CONFigure:ANALy:FRAMe:INDEx 1"
            };
            if (agc)
                cmds.Add("WT:SENSe:AGC");
            cmds.Add("WT:SENSe:CAPTure");
            string cmd = string.Join("\n", cmds) + "\n";
            //Console.Write(cmd);
            Write(cmd);
            CheckError("VSA");
        }

        public string GetResult()
        {
            var baseResult = Query("WT:WIFI:SENSe:FETCh:BASEresult?\n");
            if (!baseResult.Contains("\r\n"))
            {
                throw new Exception($"base result error no \\r\\n: {baseResult}");
            }
            return baseResult.Trim();
        }

        public void SetDevmParam(int dutyRadio, double leadTime, double delayTime)
        {
            List<string> cmds = new List<string>
            {
                $"WT:SOURce:CONFigure:DEVM:DUT:DUTY:RADIo {dutyRadio}",
                $"WT:SOURce:CONFigure:DEVM:LEAD:TIME {leadTime}",
                $"WT:SOURce:CONFigure:DEVM:DELAy:TIME {delayTime}",
                $"WT:SOURce:CONFigure:DEVM:MODE 1"
            };
            string cmd = string.Join("\n", cmds) + "\n";
            Write(cmd);
            CheckError("SetDevmParam");
        }
    }
}
