using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace LangFlowClient
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void buttonC_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textBoxNA.Text))
            {
                richTextBoxLF.Text= "❌ 错误：NATAPP公网地址不能为空！";
                return;
            }
            if (string.IsNullOrWhiteSpace(richTextBoxC.Text))
            {

            }
        }
    }
}
