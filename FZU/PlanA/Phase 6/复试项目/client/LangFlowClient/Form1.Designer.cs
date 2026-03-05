namespace LangFlowClient
{
    partial class Form1
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.textBoxNA = new System.Windows.Forms.TextBox();
            this.labelNA = new System.Windows.Forms.Label();
            this.buttonC = new System.Windows.Forms.Button();
            this.tableLayoutPanel1 = new System.Windows.Forms.TableLayoutPanel();
            this.richTextBoxLF = new System.Windows.Forms.RichTextBox();
            this.richTextBoxC = new System.Windows.Forms.RichTextBox();
            this.tableLayoutPanel1.SuspendLayout();
            this.SuspendLayout();
            // 
            // textBoxNA
            // 
            this.textBoxNA.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.textBoxNA.Location = new System.Drawing.Point(3, 33);
            this.textBoxNA.Name = "textBoxNA";
            this.textBoxNA.Size = new System.Drawing.Size(334, 25);
            this.textBoxNA.TabIndex = 0;
            // 
            // labelNA
            // 
            this.labelNA.AutoSize = true;
            this.labelNA.Dock = System.Windows.Forms.DockStyle.Fill;
            this.labelNA.Location = new System.Drawing.Point(3, 0);
            this.labelNA.Name = "labelNA";
            this.labelNA.Size = new System.Drawing.Size(334, 30);
            this.labelNA.TabIndex = 1;
            this.labelNA.Text = "NATAPP分配的公网地址";
            this.labelNA.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // buttonC
            // 
            this.buttonC.Dock = System.Windows.Forms.DockStyle.Fill;
            this.buttonC.Location = new System.Drawing.Point(3, 401);
            this.buttonC.Name = "buttonC";
            this.buttonC.Size = new System.Drawing.Size(334, 25);
            this.buttonC.TabIndex = 2;
            this.buttonC.Text = "发送";
            this.buttonC.UseVisualStyleBackColor = true;
            this.buttonC.Click += new System.EventHandler(this.buttonC_Click);
            // 
            // tableLayoutPanel1
            // 
            this.tableLayoutPanel1.ColumnCount = 1;
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutPanel1.Controls.Add(this.buttonC, 0, 4);
            this.tableLayoutPanel1.Controls.Add(this.labelNA, 0, 0);
            this.tableLayoutPanel1.Controls.Add(this.richTextBoxLF, 0, 2);
            this.tableLayoutPanel1.Controls.Add(this.textBoxNA, 0, 1);
            this.tableLayoutPanel1.Controls.Add(this.richTextBoxC, 0, 3);
            this.tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tableLayoutPanel1.Location = new System.Drawing.Point(0, 0);
            this.tableLayoutPanel1.Name = "tableLayoutPanel1";
            this.tableLayoutPanel1.RowCount = 5;
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 75F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30F));
            this.tableLayoutPanel1.Size = new System.Drawing.Size(340, 429);
            this.tableLayoutPanel1.TabIndex = 3;
            // 
            // richTextBoxLF
            // 
            this.richTextBoxLF.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richTextBoxLF.Location = new System.Drawing.Point(3, 63);
            this.richTextBoxLF.Name = "richTextBoxLF";
            this.richTextBoxLF.Size = new System.Drawing.Size(334, 248);
            this.richTextBoxLF.TabIndex = 3;
            this.richTextBoxLF.Text = "";
            // 
            // richTextBoxC
            // 
            this.richTextBoxC.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richTextBoxC.Location = new System.Drawing.Point(3, 317);
            this.richTextBoxC.Name = "richTextBoxC";
            this.richTextBoxC.Size = new System.Drawing.Size(334, 78);
            this.richTextBoxC.TabIndex = 4;
            this.richTextBoxC.Text = "";
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(340, 429);
            this.Controls.Add(this.tableLayoutPanel1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.tableLayoutPanel1.ResumeLayout(false);
            this.tableLayoutPanel1.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TextBox textBoxNA;
        private System.Windows.Forms.Label labelNA;
        private System.Windows.Forms.Button buttonC;
        private System.Windows.Forms.TableLayoutPanel tableLayoutPanel1;
        private System.Windows.Forms.RichTextBox richTextBoxLF;
        private System.Windows.Forms.RichTextBox richTextBoxC;
    }
}

