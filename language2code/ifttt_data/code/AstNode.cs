using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ifttt
{
    /// <summary>
    /// Node (subtree, really) in an abstract syntax tree.
    /// These trees might be fully instantiated, or they may contain variables
    /// </summary>
    public class AstNode
    {
        /// <summary>
        /// If nonzero, this is an id for a variable (should be unique)
        /// </summary>
        public int VariableID = 0;
        /// <summary>
        /// True if a variable, false if a constant tree node
        /// </summary>
        public bool Variable { get { return VariableID != 0; } }
        /// <summary>
        /// Node name
        /// </summary>
        public string Name;
        /// <summary>
        /// List of children.
        /// </summary>
        public List<AstNode> Children;

        /// <summary>
        /// Construct a new variable node
        /// </summary>
        /// <param name="name"></param>
        /// <param name="id"></param>
        /// <returns></returns>
        public static AstNode Var(string name, int id)
        {
            if (id < 1) throw new ArgumentException("Variable ID must be a positive integer");
            var n = new AstNode(name);
            n.VariableID = id;
            return n;
        }

        /// <summary>
        /// Get the yield of the tree -- the sequence of leaves
        /// </summary>
        public List<AstNode> Yield
        {
            get
            {
                if (Children.Count == 0) throw new ArgumentException("It is strange to ask for the yield of a leaf node");
                var l = new List<AstNode>();
                var s = new Stack<AstNode>();
                s.Push(this);
                while (s.Count > 0)
                {
                    var n = s.Pop();
                    if (n.Children.Count == 0)
                        l.Add(n);
                    else
                        foreach (var c in ((IEnumerable<AstNode>)n.Children).Reverse())
                            s.Push(c);
                }
                return l;
            }
        }

        /// <summary>
        /// Get all nodes in the tree -- pre-order, left-to-right traversal
        /// </summary>
        public IEnumerable<AstNode> Nodes
        {
            get
            {
                yield return this;
                foreach (var n in Children)
                    foreach (var nn in n.Nodes)
                        yield return nn;
            }
        }

        /// <summary>
        /// Get all the productions used in this tree -- pre-order, left-to-right traversal
        /// </summary>
        /// <returns></returns>
        public IEnumerable<AstNode> Productions()
        {
            var s = new Stack<AstNode>();

            s.Push(this);

            while (s.Count > 0)
            {
                var n = s.Pop();
                foreach (var c in ((IEnumerable<AstNode>)n.Children).Reverse())
                    s.Push(c);
                if (n.Children.Count > 0)
                {
                    var x = new AstNode(n.Name);
                    foreach (var c in n.Children)
                        x.Children.Add(new AstNode(c.Name));
                    yield return x;
                }
            }
        }

        /// <summary>
        /// Deep copy of a tree.
        /// </summary>
        /// <returns></returns>
        public AstNode DeepCopy()
        {
            var an = new AstNode(Name);
            an.VariableID = this.VariableID;
            an.Children.AddRange(Children.Select(c => c.DeepCopy()));
            return an;
        }

        /// <summary>
        /// Simple hash code.
        /// </summary>
        /// <returns></returns>
        public override int GetHashCode()
        {
            int code = this.Name.GetHashCode();
            code = code * 37 + VariableID;
            foreach (var c in Children)
                code = code * 37 + c.GetHashCode();
            return code;
        }

        /// <summary>
        /// print out in a multiline format with indenting.
        /// </summary>
        /// <returns></returns>
        public string PrettyPrint()
        {
            var sb = new StringBuilder();
            bool needsNewline = false;
            PrettyPrintHelper(sb, 0, ref needsNewline);
            return sb.ToString();
        }

        void PrettyPrintHelper(StringBuilder sb, int depth, ref bool needsNewline)
        {
            if (needsNewline)
            {
                sb.AppendLine();
                for (int i = 0; i < depth; ++i) sb.Append(' ');
                needsNewline = false;
            }

            if (Variable)
            {
                sb.Append('[');
                AppendSafeName(sb);
                sb.Append(' ');
                sb.Append(VariableID);
                sb.Append(']');
                needsNewline = true;
                return;
            }

            sb.Append('(');
            sb.Append(Name);
            if (Children.Count == 0)
            {
                sb.Append(')');
                needsNewline = true;
                return;
            }

            sb.Append(' ');
            foreach (var c in Children)
                c.PrettyPrintHelper(sb, depth + 2, ref needsNewline);
            sb.Append(')');
        }

        /// <summary>
        /// Check for deep equality.
        /// </summary>
        /// <param name="obj"></param>
        /// <returns></returns>
        public override bool Equals(object obj)
        {
            if (!(obj is AstNode)) return false;
            var an = obj as AstNode;
            if (an.GetHashCode() != this.GetHashCode()) return false;

            if (string.CompareOrdinal(Name, an.Name) != 0) return false;
            if (VariableID != an.VariableID) return false;
            if (Children.Count != an.Children.Count) return false;
            for (int i = 0; i < Children.Count; ++i)
                if (!Children[i].Equals(an.Children[i])) return false;
            return true;
        }

        /// <summary>
        /// Construct a new tree.
        /// </summary>
        /// <param name="name"></param>
        /// <param name="children"></param>
        public AstNode(string name, params AstNode[] children)
        {
            Name = name;
            Children = new List<AstNode>(children);
        }

        /// <summary>
        /// construct a tree without a name
        /// </summary>
        public AstNode() { Name = ""; Children = new List<AstNode>(); }

        /// <summary>
        /// Access children based on index.
        /// </summary>
        /// <param name="i"></param>
        /// <returns></returns>
        public AstNode this[int i] { get { return Children[i]; } }

        /// <summary>
        /// Find the first child with a given name, or null if no such child is found.
        /// </summary>
        /// <param name="s"></param>
        /// <returns></returns>
        public AstNode this[string s]
        {
            get
            {
                foreach (var c in Children)
                    if (string.CompareOrdinal(c.Name, s) == 0)
                        return c;
                return null;
            }
        }

        /// <summary>
        /// Convert to a compact single line format.
        /// </summary>
        /// <returns></returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            ToString(sb);
            return sb.ToString();
        }

        public void ToString(StringBuilder sb)
        {
            if (Variable)
            {
                sb.Append('[');
                AppendSafeName(sb);
                sb.Append(' ');
                sb.Append(VariableID);
                sb.Append(']');
                return;
            }
            sb.Append('(');
            AppendSafeName(sb);
            foreach (var c in Children)
            {
                sb.Append(' ');
                c.ToString(sb);
            }
            sb.Append(')');
        }

        /// <summary>
        /// Construct a literal for the string that uses quotes for names with spaces or special characters.
        /// </summary>
        /// <param name="sb"></param>
        public void AppendSafeName(StringBuilder sb)
        {
            if (Name.Length > 0 && !Name.Any(c => c == '\\' || c == '"' || c == '(' || c == ')' || c == '[' || c == ']' || char.IsWhiteSpace(c)))
            {
                sb.Append(Name);
                return;
            }

            sb.Append('"');
            foreach (var c in Name)
            {
                if (c == '\\' || c == '"')
                    sb.Append('\\');
                sb.Append(c);
            }
            sb.Append('"');
        }

        /// <summary>
        /// Parse a string representation of a tree into a tree.
        /// </summary>
        /// <param name="s"></param>
        /// <returns></returns>
        public static AstNode Parse(string s)
        {
            int offset = 0;
            return Parse(s, ref offset);
        }

        static AstNode Parse(string s, ref int offset)
        {
            if (s[offset] != '(')
            {
                if (s[offset] == '[') return ParseVariable(s, ref offset);
                throw new ArgumentException("malformed string: node did not start with open paren at position " + offset.ToString());
            }
            ++offset;

            var name = ReadName(s, ref offset);
            var node = new AstNode(name);
            while (true)
            {
                if (s[offset] == ')')
                {
                    ++offset;
                    return node;
                }
                if (s[offset] != ' ')
                {
                    throw new ArgumentException("malformed string: node should have either had a close paren or a space at position " + offset.ToString());
                }
                ++offset;
                node.Children.Add(Parse(s, ref offset));
            }
        }

        static AstNode ParseVariable(string s, ref int offset)
        {
            if (s[offset] != '[')
                throw new ArgumentException("malformed string: node did not start with open paren at position " + offset.ToString());
            ++offset;
            var name = ReadName(s, ref offset);
            if (s[offset] != ' ') throw new ArgumentException();
            ++offset;
            var id = ReadNumber(s, ref offset);
            if (s[offset] != ']') throw new ArgumentException();
            ++offset;
            var n = new AstNode(name);
            n.VariableID = id;
            return n;
        }

        private static int ReadNumber(string s, ref int offset)
        {
            int end = offset;
            while (char.IsDigit(s[end]))
                ++end;
            int num = int.Parse(s.Substring(offset, end - offset));
            offset = end;
            return num;
        }

        private static string ReadName(string s, ref int offset)
        {
            StringBuilder sb = new StringBuilder();
            if (s[offset] == '\"')
            {
                ++offset;
                while (s[offset] != '\"')
                {
                    if (s[offset] == '\\')
                        ++offset;
                    sb.Append(s[offset++]);
                }
                ++offset;
            }
            else
            {
                while (s[offset] != ' ' && s[offset] != ')')
                    sb.Append(s[offset++]);
            }
            return sb.ToString();
        }
    }
}
